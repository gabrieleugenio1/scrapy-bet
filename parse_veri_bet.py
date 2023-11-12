from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lxml import etree 
from datetime import datetime

import re
import json

# URL da página que queremos fazer scraping
url = "https://veri.bet/odds-picks?filter=upcoming"

# Configuração do serviço do ChromeDriver
chrome_path = "./chromedriver.exe"  
service = ChromeService(executable_path=chrome_path)

# Configuração do cabeçalho da solicitação com o user agent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

# Inicializar o navegador Chrome usando o Selenium
driver = webdriver.Chrome(service=service)
driver.get(url)

# Aguardar até que a tabela seja carregada
try:
    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'col.col-md'))
    WebDriverWait(driver, 50).until(element_present)
except Exception as e:
    print("Erro ao esperar pelo carregamento da tabela:", e)

page_source = driver.page_source
driver.quit()

# Utilizar o BeautifulSoup para fazer o parsing do HTML
soup = BeautifulSoup(page_source, "html.parser")

# Encontrar os elementos HTML 
dom = etree.HTML(str(soup)) 
all_names = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]//span')
names = [name.text.strip() for name in all_names]

all_categories = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "text-left", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
category  = [category.strip() for category in all_categories if category != '\n']

all_dates = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "badge-light", " " )) and contains(concat( " ", @class, " " ), concat( " ", "text-left", " " ))]/text()')
dates  = [date.strip() for date in all_dates if date != '\n']

all_periods = dom.xpath('//div//table//tbody//tr[1]//td[1]//*[contains(concat(" ", @class, " "), "text-muted")]/text()')
periods  = [period.strip() for period in all_periods if period != '\n']
periods = list(filter(lambda x: re.search(r'ODDS', x), periods))
periods = [re.sub(r'\n\t+', '', element) for element in periods]
periods = [element.replace('ODDS', '').strip() for element in periods]

all_moneyline_team_one = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
moneyline_team_one  = [team_one.strip() for team_one  in all_moneyline_team_one if team_one  != '\n']

all_moneyline_team_two = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
moneyline_team_two  = [team_two.strip() for team_two  in all_moneyline_team_two if team_two  != '\n']

all_spread_team_one = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
spread_team_one  = [team_one_spread.strip() for team_one_spread  in all_spread_team_one if team_one_spread  != '\n']
spread_team_one = [re.sub(r'\n\t+', '', element) for element in spread_team_one] 

all_spread_team_two = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
spread_team_two  = [team_two_spread.strip() for team_two_spread  in all_spread_team_two if team_two_spread  != '\n']
spread_team_two = [re.sub(r'\n\t+', '', element) for element in spread_team_two]


all_total_team_one = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
total_team_one  = [team_one_total.strip() for team_one_total  in all_total_team_one if team_one_total  != '\n']
total_team_one = [re.sub(r'O\n\t+', '', element) for element in total_team_one]

all_total_team_two = dom.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//td[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-muted", " " ))]/text()')
total_team_two  = [team_two_total.strip() for team_two_total  in all_total_team_two if team_two_total  != '\n']
total_team_two = [re.sub(r'U\n\t+', '', element) for element in total_team_two]

# Combinar os nomes 
results = []
for i in range(0, len(names), 2):
    par = [names[i], names[i + 1]]
    results.append(par)

utc_iso_dates = []
for date_str in dates:
    # Pegar horário e período
    time_part, period_part = date_str.split(" ")[0], date_str.split(" ")[1]

    if "(" in date_str and ")" in date_str:
        # Extrair a parte da data da string
        date_part = date_str.split("(")[1].split(")")[0].strip()

        # Converter a data para datetime
        dt = datetime.strptime(date_part, "%m/%d/%Y")
        dt = dt.replace(hour=(int(time_part.split(":")[0]) + 12) % 24 if period_part == "PM" else int(time_part.split(":")[0]),
                        minute=int(time_part.split(":")[1]))
    else:
        # Assumir que a data é para o dia atual
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dt = today.replace(hour=(int(time_part.split(":")[0]) + 12) % 24 if period_part == "PM" else int(time_part.split(":")[0]),
                           minute=int(time_part.split(":")[1]))

    # Formatar como ISO
    utc_iso_dates.append(dt.isoformat())


spread_list_one = []
spread_list_two = []
total_list_one = []
total_list_two = []
valor_anterior= None


for elemento in spread_team_one:
    if elemento.startswith('-') or elemento.startswith('+'):
        # Se o elemento tiver um sinal de "-" e conter um "+" atualiza o valor anterior
        valor_anterior = elemento
    elif isinstance(elemento, str) and elemento.startswith('(') and ')' in elemento:
        # Se o elemento estiver entre parênteses, extrair o número e concatenar com o valor anterior
        spread_list_one.append(f"{valor_anterior} {elemento}")
        valor_anterior = None
    else:
        # Caso não, adicionar o elemento a nova lista
        spread_list_one.append(elemento)

valor_anterior = None

for elemento in spread_team_two:
    if elemento.startswith('-') or elemento.startswith('+'):
        valor_anterior = elemento
    elif isinstance(elemento, str) and elemento.startswith('(') and ')' in elemento:
        spread_list_two.append(f"{valor_anterior} {elemento}")
        valor_anterior = None
    else:
        spread_list_two.append(elemento)

valor_anterior = None


for elemento in total_team_one:
    try:
        #Verificar se é um número
        valor_float = float(elemento)
        valor_anterior = elemento
    except ValueError:
        if isinstance(elemento, str) and elemento.startswith('(') and ')' in elemento:
            total_list_one.append(f"{valor_anterior} {elemento}")
            valor_anterior = None
        else:
            total_list_one.append(elemento)

valor_anterior = None

for elemento in total_team_two:
    try:
        valor_float = float(elemento)        
        valor_anterior = elemento
    except ValueError:
        if isinstance(elemento, str) and elemento.startswith('(') and ')' in elemento:
            total_list_two.append(f"{valor_anterior} {elemento}")
            valor_anterior = None
        else:
            total_list_two.append(elemento)

for i in range(len(results)):
    results[i].append(category[i]) 
    results[i].append(utc_iso_dates[i]) 
    results[i].append(periods[i]) 
    results[i].append(moneyline_team_one[i]) 
    results[i].append(moneyline_team_two[i])  
    results[i].append(spread_list_one[i]) 
    results[i].append(spread_list_two[i])  
    results[i].append(total_list_one[i]) 
    results[i].append(total_list_two[i])  


data = []

for i in results:
    sport_league = i[2]
    event_date = i[3]
    team_1 = i[0]
    team_2 = i[1]
    pitcher = ''
    period = i[4]

    price_moneyline_team_1 = i[5]
    price_moneyline_team_2 = i[6]


    spread_team_1 = 'N/A'
    price_spread_team_1 = 'N/A'
    spread_team_2 = 'N/A'
    price_spread_team_2 = 'N/A'

    total_over_team_1 = 'N/A'
    price_total_team_1 = 'N/A'
    total_under_team_2 = 'N/A'
    price_total_team_2 = 'N/A'

    if i[7] != 'N/A':
        spread_all = i[7].split(' ')
        spread_team_1 = spread_all[0]      
        price_spread_team_1 = spread_all[1].replace('(', '').replace(')', '')

    if i[8] != 'N/A':
        spread_all = i[8].split(' ')
        spread_team_2 = spread_all[0]      
        price_spread_team_2 = spread_all[1].replace('(', '').replace(')', '')
            
    if i[9] != 'N/A':
        total_all = i[9].split(' ')
        print(total_all)
        total_over_team_1 = total_all[0]      
        price_total_team_1 = total_all[1].replace('(', '').replace(')', '')
        print(i[9])

    if i[10] != 'N/A':
        total_all = i[10].split(' ')
        total_under_team_2 = total_all[0]      
        price_total_team_2 = total_all[1].replace('(', '').replace(')', '')



    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'moneyline',        
        'price': price_moneyline_team_1,            
        'side': team_1,             
        'team': team_1,             
        'spread': 0     
    }) 
    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'moneyline',        
        'price': price_moneyline_team_2,            
        'side': team_2,             
        'team': team_2,             
        'spread': 0      
    }) 

    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'spread',        
        'price': price_spread_team_1,            
        'side':  team_1,
        'team':  team_1,
        'spread': spread_team_1      
    }) 
    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'spread',        
        'price': price_spread_team_2,            
        'side':  team_2,
        'team':  team_2,
        'spread': spread_team_2      
    }) 

    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'over/under',        
        'price': price_total_team_1,            
        'side':  'over',
        'team':  team_1,
        'spread': total_over_team_1      
    }) 
    data.append({
        'sport_league': sport_league,     
        'event_date_utc': event_date,   
        'team1': team_1,            
        'team2': team_2,            
        'pitcher': '',          
        'period': period,           
        'line_type': 'over/under',        
        'price': price_total_team_2,            
        'side':  'under',
        'team':  team_2,
        'spread': total_under_team_2 
    }) 

# Criar o JSON a partir dos dados
json_data = json.dumps(data, indent=2) 

# Salvar o JSON em um arquivo
with open("veri.json", "w") as arquivo_json:
    arquivo_json.write(json_data)
    
print(json_data) 
