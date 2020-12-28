import re
import sys
import requests
import pandas as pd 
import pytz
from bs4 import BeautifulSoup
from live_functions import current_live_games
from fixtures_functions import display_fixtures, print_divider

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

def main():
    print_divider()
    print("Welcome to Live EPL")
    print_divider()
    while True:
        try:
            command = input("Enter a command: ")
            print_divider()
        except EOFError:
            print("\nSuccessfully Exited")
            break
        except KeyboardInterrupt:
            print("\nSuccessfully Exited")
            break
        if command == 'standings':
            print(standings_table)
        elif command == 'fixtures':
            display_fixtures()
        elif command == 'live':
            current_live_games()
        elif command == 'help':
            print('HELP MENU')
            print('--------------')
            print("'standings' --> Displays the current table positions of each team")
            print("'fixtures' --> Displays upcoming fixtures and scores from today")
            print("'live' --> Displays a list of current live games and respective commentary depending on user input")
        elif command == 'exit':
            print("Successfully Exited")
            break
        else:
            print(command + " is not a valid command.")
            print("Please type a valid command or type in 'help' for a list of commands")
        print_divider()
        
standings_table = create_standings()
main()