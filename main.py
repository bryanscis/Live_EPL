import os
import re
import sys
import requests
import pandas as pd 
import pytz
from datetime import date, datetime
from bs4 import BeautifulSoup

def create_standings():
    page = requests.get("https://www.espn.com/soccer/table/_/league/eng.1")
    soup = BeautifulSoup(page.content, 'html.parser')
    table1 = soup.find_all('table')[0].find_all('tr')
    teams = []
    for team in table1:
        team_name = re.search(r'img alt="([^"]*)', str(team))
        if team_name:
            team_name = team_name.group(1)
            team_name = re.sub(r'&amp;', '&', str(team_name))
            teams.append(team_name)
    table2 = soup.find_all('table')[1].find_all('tr')
    statistics= {}
    table_position = 0
    for team in table2:
        team_statistics = re.findall(r'>([0-9]+)<', str(team))
        if team_statistics:
            statistics[teams[table_position]] = team_statistics
            table_position += 1
    rows = ['Games Played', 'Wins', 'Draws', 'Losses', 'Goals For', 'Goals Against', 'Points']
    standings = pd.DataFrame(statistics, index=rows, columns=teams).transpose()
    standings['Goal Difference'] = standings['Goals For'].astype(int) - standings['Goals Against'].astype(int)
    return standings

def convert_time(time):
    pytz_time = datetime.strptime(uk_time, '%Y-%m-%d %H:%M:%S')
    tz_ldn = pytz.timezone('Europe/London')
    tz_la = pytz.timezone('America/Los_Angeles')
    ldn_time = tz_ldn.localize(pytz_time)
    la_time = ldn_time.astimezone(tz_la)
    return la_time.time()

today = re.sub(r'-', '', str(date.today()))
page = requests.get('https://www.espn.com/soccer/fixtures/_/date/' + today + '/league/eng.1')
soup = BeautifulSoup(page.content, 'html.parser')
count = 0
while True:
    try:
        fixtures = soup.find_all('table')[count].find_all('tr')
        date_caption = soup.find_all('h2', class_= 'table-caption')[count]
        date = re.search(r'>([^+]*)<', str(date_caption)).group(1)
    except:
        break
    print(date)
    print("--------------------------------------------")
    for element in fixtures[1:]:
        spans = element.find_all('span')
        team1 = re.search(r'>([^+]*)<' ,str(spans[0]))
        team2 = re.search(r'>([^+]*)<' ,str(spans[-1]))
        time = re.search(r'([\d]+-[\d]+-[\d]+)T([\d]+:[\d]+)Z', str(element))
        uk_time = time.group(1) + " " + time.group(2) + ":00"
        cur_time = str(convert_time(uk_time))
        if team1 and team2:
            print(team1.group(1) + ' vs ' + team2.group(1) + ' at ' + cur_time + ' Los Angeles Time')
    print("--------------------------------------------")
    count += 1
    
def main():
    print("Welcome to Live EPL")
    print("--------------------------------------------")
    while True:
        try:
            command = input("Enter a command: ")
        except EOFError:
            print("\nSuccessfully Exited")
            break
        except KeyboardInterrupt:
            print("\nSuccessfully Exited")
            break
        if command == 'standings':
            print(standings_table)
        elif command == 'exit':
            print("\nSuccessfully Exited")
            break
        else:
            print(command + " is not a valid command.")
            print("Please type a valid command.")
            print("Type in 'help' for list of commands.")
        print("--------------------------------------------")

standings_table = create_standings()
main()