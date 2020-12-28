import pytz
import requests
import re
from bs4 import BeautifulSoup
from datetime import date, datetime

def convert_time(time):
    pytz_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    tz_ldn = pytz.timezone('Europe/London')
    tz_la = pytz.timezone('America/Los_Angeles')
    ldn_time = tz_ldn.localize(pytz_time)
    la_time = ldn_time.astimezone(tz_la)
    return la_time.time()

def team_string_check(name):
    return re.sub(r'&amp;', '&', name)

def print_divider():
    print("-------------------------------------------------------------------")

def display_fixtures():
    page = requests.get('https://www.espn.com/soccer/fixtures/_/league/eng.1')
    soup = BeautifulSoup(page.content, 'html.parser')
    count = 0
    while True:
        try:
            fixtures = soup.find_all('table')[count].find_all('tr')
            date_caption = soup.find_all('h2', class_= 'table-caption')
            if count != 0:
                print_divider()
        except: 
            break
        print(date_caption[count].get_text())
        print_divider()
        for element in fixtures[1:]:
            spans = element.find_all('span')
            team1 = re.search(r'>([^+]*)<' ,str(spans[0]))
            team2 = re.search(r'>([^+]*)<' ,str(spans[-1]))
            if element.find('td', class_='live'):
                if team1 and team2:
                    print(team_string_check(str(team1.group(1)))
                        + ' vs ' + team_string_check(str(team2.group(1))) 
                        + ' is LIVE right now in Los Angeles Time')
            elif element.find( attrs={'name': ('&lpos=eng.1:schedule:score')}):
                final_score = element.find('span', class_='record').get_text()
                if team1 and team2:
                    print(team_string_check(str(team1.group(1)))
                        + ' vs ' + team_string_check(str(team2.group(1))) 
                        + ' ended in ' + final_score)
            else:
                time = re.search(r'([\d]+-[\d]+-[\d]+)T([\d]+:[\d]+)Z', str(element))
                uk_time = time.group(1) + " " + time.group(2) + ":00"
                cur_time = str(convert_time(uk_time))
                if team1 and team2:
                    print(team_string_check(str(team1.group(1)))
                        + ' vs ' + team_string_check(str(team2.group(1))) 
                        + ' at ' + cur_time + ' Los Angeles Time')
        count += 1