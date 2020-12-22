import os
import re
import sys
import requests
import pandas as pd
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