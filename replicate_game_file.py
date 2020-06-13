## packages ##
import pandas as pd
import numpy
import datetime

import requests
from bs4 import BeautifulSoup
import time
import random

## folder structure ##
data_folder = '/Users/robertgreer/Documents/Coding/NFL/Data Sources/Legacy PBP'

game_folder_path = '{0}/game'.format(data_folder)
pbp_data_location = '{0}/legacy_pbp.csv'.format(data_folder)


## set starting season ##
starting_season = 1999
current_season = starting_season


## set max season ##
if datetime.date.today().month > 8:
    ending_season = datetime.date.today().year
else:
    ending_season = datetime.date.today().year - 1


## dict for renaming teams ##
standardize_dict = {

    'Arizona Cardinals' : 'ARI',
    'Atlanta Falcons' : 'ATL',
    'Baltimore Ravens' : 'BAL',
    'Buffalo Bills' : 'BUF',
    'Carolina Panthers' : 'CAR',
    'Chicago Bears' : 'CHI',
    'Cincinnati Bengals' : 'CIN',
    'Cleveland Browns' : 'CLE',
    'Dallas Cowboys' : 'DAL',
    'Denver Broncos' : 'DEN',
    'Detroit Lions' : 'DET',
    'Green Bay Packers' : 'GB',
    'Houston Texans' : 'HOU',
    'Indianapolis Colts' : 'IND',
    'Jacksonville Jaguars' : 'JAX',
    'Kansas City Chiefs' : 'KC',
    'Los Angeles Chargers' : 'LAC',
    'Los Angeles Rams' : 'LAR',
    'Miami Dolphins' : 'MIA',
    'Minnesota Vikings' : 'MIN',
    'New England Patriots' : 'NE',
    'New Orleans Saints' : 'NO',
    'New York Giants' : 'NYG',
    'New York Jets' : 'NYJ',
    'Oakland Raiders' : 'OAK',
    'Philadelphia Eagles' : 'PHI',
    'Pittsburgh Steelers' : 'PIT',
    'San Diego Chargers' : 'LAC',
    'San Francisco 49ers' : 'SF',
    'Seattle Seahawks' : 'SEA',
    'St. Louis Rams' : 'LAR',
    'Tampa Bay Buccaneers' : 'TB',
    'Tennessee Titans' : 'TEN',
    'Washington Redskins' : 'WAS',

}



## pull game links ##
data_rows = []
while current_season <= ending_season:
    time.sleep((2.5 + random.random() * 5))
    url = ' https://www.pro-football-reference.com/years/{0}/games.htm'.format(current_season)
    raw = requests.get(url)
    parsed = BeautifulSoup(raw.content, "html.parser")
    game_table = parsed.find_all('table', {'id' : 'games'})[0]
    playoff_skip = False
    season_rows = []
    for row in game_table.find_all('tbody')[0].find_all('tr'):
        if row.has_attr('class'):
            if row['class'] == 'thead': ## skip week dividers ##
                pass
            else:
                if row['class'] == 'rowSum': ## skip playoff divider ##
                    playoff_skip = True
                else:
                    pass
        elif playoff_skip: ## skip playoffs ##
            pass
        else:
            if row.find_all('td', {'data-stat' : 'game_date'})[0].text == 'Playoffs':  ## earlier years dont catch ##
                playoff_skip = True
            else:
                ## determine home teams and scores ##
                if row.find_all('td', {'data-stat' : 'game_location'})[0].text == '@':
                    home_team = row.find_all('td', {'data-stat' : 'loser'})[0].text
                    away_team = row.find_all('td', {'data-stat' : 'winner'})[0].text
                    home_score = int(row.find_all('td', {'data-stat' : 'pts_lose'})[0].text)
                    away_score = int(row.find_all('td', {'data-stat' : 'pts_win'})[0].text)
                else:
                    away_team = row.find_all('td', {'data-stat' : 'loser'})[0].text
                    home_team = row.find_all('td', {'data-stat' : 'winner'})[0].text
                    away_score = int(row.find_all('td', {'data-stat' : 'pts_lose'})[0].text)
                    home_score = int(row.find_all('td', {'data-stat' : 'pts_win'})[0].text)
                home_team = standardize_dict[home_team]
                away_team = standardize_dict[away_team]
                row_data = {
                    'type' : 'reg',
                    'home_team' : home_team,
                    'away_team' : away_team,
                    'home_score' : home_score,
                    'away_score' : away_score,
                    'week' : int(row.find_all('th', {'data-stat' : 'week_num'})[0].text),
                    'season' : current_season,
                    'state_of_game' : 'POST'
                }
                data_rows.append(row_data)
                season_rows.append(row_data)
    season_df = pd.DataFrame(season_rows)
    season_df.to_csv('{0}/reg_games_raw_{1}.csv'.format(game_folder_path, current_season))
    current_season += 1


game_df = pd.DataFrame(data_rows)


## add game center IDs ##
## load pbp data ##
pbp_df = pd.read_csv(pbp_data_location, low_memory=False, index_col=0)

## establish season ##
pbp_df['year'] = pbp_df['game_date'].str.split('-').str[0].astype(int)
pbp_df['month'] = pbp_df['game_date'].str.split('-').str[1].astype(int)
pbp_df['season'] = numpy.where(pbp_df['month'] > 8, pbp_df['year'], pbp_df['year'] - 1)

## standardize team name ##
pbp_team_standard_dict = {

    'ARI' : 'ARI',
    'ATL' : 'ATL',
    'BAL' : 'BAL',
    'BUF' : 'BUF',
    'CAR' : 'CAR',
    'CHI' : 'CHI',
    'CIN' : 'CIN',
    'CLE' : 'CLE',
    'DAL' : 'DAL',
    'DEN' : 'DEN',
    'DET' : 'DET',
    'GB'  : 'GB',
    'HOU' : 'HOU',
    'IND' : 'IND',
    'JAC' : 'JAX',
    'JAX' : 'JAX',
    'KC'  : 'KC',
    'LA'  : 'LAR',
    'LAC' : 'LAC',
    'MIA' : 'MIA',
    'MIN' : 'MIN',
    'NE'  : 'NE',
    'NO'  : 'NO',
    'NYG' : 'NYG',
    'NYJ' : 'NYJ',
    'OAK' : 'OAK',
    'PHI' : 'PHI',
    'PIT' : 'PIT',
    'SD'  : 'LAC',
    'SEA' : 'SEA',
    'SF'  : 'SF',
    'STL' : 'LAR',
    'TB'  : 'TB',
    'TEN' : 'TEN',
    'WAS' : 'WAS',

}

pbp_df['home_team'] = pbp_df['home_team'].replace(pbp_team_standard_dict)
pbp_df['away_team'] = pbp_df['away_team'].replace(pbp_team_standard_dict)

## get unique games ##
pbp_df = pbp_df[[
    'season',
    'game_id',
    'home_team',
    'away_team'
]].drop_duplicates()


## attach ##
new_game_df = pd.merge(
    game_df,
    pbp_df,
    on=[
        'season',
        'home_team',
        'away_team'
    ],
    how='left'
)

## add gamecenter link ##
new_game_df['game_url'] = 'http://www.nfl.com/liveupdate/game-center/' + new_game_df['game_id'].astype('str') + '/' +new_game_df['game_id'].astype('str') +'_gtd.json'

## order cols & export ##
new_game_df[[
    'type',
    'game_id',
    'home_team',
    'away_team',
    'week',
    'season',
    'state_of_game',
    'game_url',
    'home_score',
    'away_score'
]].to_csv('{0}/games.csv'.format(data_folder))
