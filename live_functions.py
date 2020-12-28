import re
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime

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
            print('[' + str(counter) + ']' + ': ' + game + '\n')
            game_dict[counter] = game_id
            counter += 1
        while True:
            try:
                user_game = int(input('Which live game would you like to choose from? '))
            except ValueError:
                print('Please type in a valid number.')
            except KeyboardInterrupt:
                print(' Back to command')
                break
            try:
                get_commentary('https://www.espn.com/soccer/commentary?gameId=' + game_dict[user_game])
                break
            except KeyError:
                print('There is no game with that number. Please type in a valid number.')