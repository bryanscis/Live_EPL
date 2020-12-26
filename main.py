import os
import re
import sys
import requests
import pandas as pd 
import pytz
from datetime import date, datetime
from bs4 import BeautifulSoup

def team_string_check(name):
    return re.sub(r'&amp;', '&', name)

def create_standings():
    page = requests.get("https://www.espn.com/soccer/table/_/league/eng.1")
    soup = BeautifulSoup(page.content, 'html.parser')
    table1 = soup.find_all('table')[0].find_all('tr')
    teams = []
    for team in table1:
        team_name = re.search(r'img alt="([^"]*)', str(team))
        if team_name:
            team_name = team_string_check(str(team_name.group(1)))
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
    pytz_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    tz_ldn = pytz.timezone('Europe/London')
    tz_la = pytz.timezone('America/Los_Angeles')
    ldn_time = tz_ldn.localize(pytz_time)
    la_time = ldn_time.astimezone(tz_la)
    return la_time.time()

def display_upcoming_fixtures():
    today = re.sub(r'-', '', str(date.today()))
    page = requests.get('https://www.espn.com/soccer/fixtures/_/date/' + today + '/league/eng.1')
    soup = BeautifulSoup(page.content, 'html.parser')
    count = 0
    while True:
        try:
            fixtures = soup.find_all('table')[count].find_all('tr')
            date_caption = soup.find_all('h2', class_= 'table-caption')[count]
            date_of_match = re.search(r'>([^+]*)<', str(date_caption)).group(1)
            print("--------------------------------------------")
        except:
            break
        print(date_of_match)
        print("--------------------------------------------")
        for element in fixtures[1:]:
            spans = element.find_all('span')
            team1 = re.search(r'>([^+]*)<' ,str(spans[0]))
            team2 = re.search(r'>([^+]*)<' ,str(spans[-1]))
            time = re.search(r'([\d]+-[\d]+-[\d]+)T([\d]+:[\d]+)Z', str(element))
            uk_time = time.group(1) + " " + time.group(2) + ":00"
            cur_time = str(convert_time(uk_time))
            if team1 and team2:
                print(team_string_check(str(team1.group(1)))
                      + ' vs ' + team_string_check(str(team2.group(1))) 
                      + ' at ' + cur_time + ' Los Angeles Time')
        count += 1
    
def main():
    print("Welcome to Live EPL")
    print("--------------------------------------------")
    while True:
        try:
            command = input("Enter a command: ")
            print("--------------------------------------------")
        except EOFError:
            print("\nSuccessfully Exited")
            break
        except KeyboardInterrupt:
            print("\nSuccessfully Exited")
            break
        if command == 'standings':
            print(standings_table)
        elif command == 'fixtures':
            display_upcoming_fixtures()
        elif command == 'live':
            current_live_games()
        elif command == 'exit':
            print("Successfully Exited")
            break
        else:
            print(command + " is not a valid command.")
            print("Please type a valid command or type in 'help' for a list of commands")
        print("--------------------------------------------")

def get_commentary(url):
    last_minute = 0
    comment = ''
    while comment.startswith('Match ends') is not True:
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            commentary= soup.find('div', class_='accordion active', id='match-commentary-1-tab-1')
            minute = commentary.find_all(attrs={'data-id': ('comment-' + str(last_minute))})
            time_stamp = minute[0].find(class_='time-stamp').get_text()
            comment = minute[0].find(class_='game-details').get_text().strip()
            print(time_stamp + ": " + comment)
            last_minute += 1
        except IndexError:
            continue
        except KeyboardInterrupt:
            print('  Back to command')
            break
        
# def find_live_games():
#     today = re.sub(r'-', '', str(datetime.today()))
#     page = requests.get('https://www.espn.com/soccer/fixtures/_/date/' + '20201201' + '/league/eng.1')
#     soup = BeautifulSoup(page.content, 'html.parser')
#     all_fixtures = soup.find('div', id='sched-container')
#     fixtures_today = all_fixtures.find_all('a', attrs={'name' : ('&lpos=eng.1:schedule:score')})
#     live_fixtures = []
#     for element in fixtures_today:
#         if element.get_text() != 'FT' or element.get_text() != 'Postponed':
#             live_fixtures.append(re.search(r'=(\d+)', element['href']).group(1))
#     print(live_fixtures)
#     return live_fixtures

def find_live_games():
    today = re.sub(r'-', '', str(date.today()))
    page = requests.get('https://www.espn.com/soccer/fixtures/_/date/' + today + '/league/eng.1')
    soup = BeautifulSoup(page.content, 'html.parser')
    all_fixtures = soup.find('div', id='sched-container')
    fixtures_today = all_fixtures.find_all('tr', class_=True)
    live_fixtures = {}
    for element in fixtures_today:
        team_names = element.find_all('a', attrs={'name': ('&lpos=eng.1:schedule:team')})
        match = team_names[0].get_text() + ' vs ' + team_names[1].get_text()
        match_status = element.find('a', attrs={'name': ('&lpos=eng.1:schedule:live')})
        #match_status = element.find('a', attrs={'name': ('&lpos=eng.1:schedule:score')})
        if match_status is not None and match_status.get_text() == 'LIVE':
            live_fixtures[match]=(re.search(r'=(\d+)', match_status['href']).group(1))
    return live_fixtures

def current_live_games():
    live_games = find_live_games()
    if not live_games:
        print('There are currently no live games.')
    else:
        game_dict = {}
        counter = 1
        for game, game_id in live_games.items():
            print('[' + str(counter) + ']' + ': ' + game)
            game_dict[counter] = game_id
            counter += 1
        user_game = input('Which live game would you like to choose from? ')
        get_commentary('https://www.espn.com/soccer/commentary?gameId=' + game_dict[int(user_game)])
        
standings_table = create_standings()
main()