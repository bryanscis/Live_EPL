import os
import re
import requests
from bs4 import BeautifulSoup

page = requests.get("https://www.espn.com/soccer/table/_/league/eng.1")

soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find_all('table')[0].find_all('tr')
table_position = 0; 
for team in table:
    team_name = re.search(r'img alt="([^"]*)', str(team))
    if team_name:
        team_name = team_name.group(1)
        team_name = re.sub(r'&amp;', '&', str(team_name))
        table_position += 1
        print(team_name)
        print(table_position)