import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression


def get_qb_data(year=2020):

    URL = "https://www.pro-football-reference.com/years/" +str(year) + "/passing.htm"
    #read in html tables which is stored as a list in all_tables
    all_tables = pd.read_html(URL)

    #selecting out the relevant table from our list
    qb_df = all_tables[0]

    #dropping column names which are inputted periodically into the dataset
    qb_df = qb_df[qb_df['Rk']!='Rk']

    #subsetting out columns that I want to keep in my df
    cols_to_keep = ['Rk', 'Player', 'Tm', 'Pos', 'G', 'GS', 'Cmp', 'Att',
           'Cmp%', 'Yds', 'TD', 'TD%', 'Int', 'Int%', 'Y/A',
           'Y/C', 'Y/G']
    qb_df = qb_df[cols_to_keep]

    #renaming columns to more readable names
    col_names = {'Rk':'qb rank', 'Player':'name', 'Tm':'team',  'Pos':'position',
                'G':'games played', 'GS':'games started', 'Cmp':'completions', 'Att':'attempts',
           'Cmp%':'completion percent', 'Yds':'yards gained', 'TD':'td', 'TD%':'td percent',
           'Int':'int', 'Int%':'int percent', 'Y/A':'yards per pass attempt',
           'Y/C':'yards per completion', 'Y/G':'yards per game'}
    qb_df.rename(columns=col_names, inplace=True)

    #converting column data to the correct class for analysis
    convert_col_int = ['games played',
           'games started', 'completions', 'attempts', 'completion percent',
           'yards gained', 'td', 'td percent', 'int', 'int percent',
           'yards per pass attempt', 'yards per completion', 'yards per game']
    convert_col_str = ['name', 'team', 'position']

    #loopoing through columns which have string data and converting values to string
    for i in convert_col_str:
        qb_df[i] = qb_df[i].astype('str')
        qb_df[i] = qb_df[i].str.lower()
        qb_df[i].replace('', np.NaN, inplace = True)

    #looping through columns with numbers and converting to int class
    for i in convert_col_int:
        qb_df[i] = qb_df[i].astype('float64')

    #subsetting out only starting QBs, i.e. those that have started at least half of the season
    qb_starters = qb_df[qb_df['games started']>=8]

    #subsetting out only quarterbacks from the df as other positions also are included
    qb_starters = qb_starters[qb_starters['position']=='qb']

    #cleaning special characters from player names
    qb_starters['name'].replace(' \*', "", inplace=True, regex=True)

    #creating a list of all qb names in order to subsett out qb players in the second rushing dataframe
    qb_starter_names = qb_starters['name']

    #reading in the table for rushing data for the 2020 season
    URL = "https://www.pro-football-reference.com/years/" +str(year) + "/rushing.htm"
    all_tables = pd.read_html(URL)

    #subsetting out the table that I want
    rush_df = all_tables[0]
    rush_df.reset_index(inplace=True)

    #column names for some reason were multi-indexed
    #getting the correct column names in the second level and setting column names to correct lables
    column_names = rush_df.columns.get_level_values(1)
    rush_df.columns = column_names

    #removing random rows
    rush_df = rush_df[rush_df['Rk']!='Rk']

    #subsetting out relevant columns for analysis
    cols_to_keep = ['Player', 'Pos', 'G', 'GS', 'Att',
                    'Yds', 'TD', 'Y/A', 'Y/G']
    rush_df = rush_df[cols_to_keep]

    #setting columns with numerical values as class int64
    for i in ['G', 'GS', 'Att', 'Yds', 'TD', 'Y/A', 'Y/G']:
        rush_df[i] = rush_df[i].astype('float64')

    #renaming column names to more readable names
    col_names = {'Player':'name', 'Pos':'position', 'Att':'rushing attempts',
                'Yds':'rushing yards', 'TD':'rushing td', 'Y/A':'rush yards per attempt', 'Y/G':"rush yards per game"}
    rush_df.rename(columns=col_names, inplace=True)

    #removing extra characters from players' names
    rush_df['name'].replace(' \*', '', inplace=True, regex=True)

    #setting columns with string values to strings and converting to lowercase
    rush_df['position'] = rush_df['position'].astype('str')
    rush_df['position'] = rush_df['position'].str.lower()
    rush_df['name'] = rush_df['name'].str.lower()

    #subsetting out only qb's from the df
    rush_df = rush_df[rush_df['position']=='qb']

    #additional cleaning on player names to remove additional special characters
    rush_df['name'].replace('\+', '', regex=True, inplace=True)
    rush_df['name'].replace('\*', '', regex=True, inplace=True)
    qb_starters['name'].replace('\+', '', regex=True, inplace=True)
    qb_starters['name'].replace('\*', '', regex=True, inplace=True)
    #only keeping qb's in the rushing df that are also in the starting quarterback dataframe
    rush_df = rush_df[rush_df['name'].isin(qb_starter_names)]

    #merging the starting qb dataframe with the rushing dataframe
    qb_starters = qb_starters.merge(rush_df, how='left', on=['name', 'position'])


    #setting fantasy points varaibles for calculating a qb's total fantasy points for the season
    pass_yards_per_point = 25
    points_per_pass_td = 4
    rush_yards_per_point = 10
    point_per_rush_td = 6

    #creating new column which has total fantasy points a qb has scored
    qb_starters['fantasy_points'] = (qb_starters['rushing yards']/rush_yards_per_point) + (qb_starters['rushing td']*point_per_rush_td) + (qb_starters['yards gained']/pass_yards_per_point) + (qb_starters['td']*points_per_pass_td)
    #creating a new column for fantasy points per game for easier analysis
    qb_starters['fantasy_points/game'] = qb_starters['fantasy_points']/qb_starters['games started']
    #creating a new column for pass attempts per game for easier analysis
    qb_starters['pass attempts/game'] = qb_starters['attempts']/qb_starters['games started']
    return(qb_starters)

qb_2020 = get_qb_data(2020)
qb_2019 = get_qb_data(2019)
qb_2018 = get_qb_data(2018)



#calculating the average passes thrown per game for all nfl quarterbacks in the 2020 season
avg_passes_thrown_2020 = [qb_2020['pass attempts/game'].mean()] * len(qb_2020)

#sorting data by fantasy points scored
qb_2020.sort_values('fantasy_points/game', ascending=False, inplace=True)

#splitting out qbs based on their fantasy football positions
top_10 = qb_2020.iloc[0:10][['name', 'fantasy_points/game', 'pass attempts/game',
                                'rush yards per game']]
avg_qbs = qb_2020.iloc[10:20][['name', 'fantasy_points/game', 'pass attempts/game',
                                'rush yards per game']]
#print(top_10)
#print(avg_qbs)
def YoY_qb_performance(current_year, previous_year, variable = 'fantasy_points'):
    qb_names = previous_year['name']
    current_year = current_year[current_year['name'].isin(qb_names)]
    previous_year = previous_year[previous_year['name'].isin(qb_2020['name'])]
    previous_year['previous_fantasy_points'] = previous_year['fantasy_points/game']
    current_year = current_year[['name', 'fantasy_points/game']]
    previous_year = previous_year[['name', 'previous_fantasy_points']]
    current_year = current_year.merge(previous_year, how='left', on='name')
    X = current_year[ 'previous_fantasy_points'].to_numpy().reshape((-1,1))
    y = current_year['fantasy_points/game']
    reg = LinearRegression().fit(X,y)
    print(reg.score(X,y))
    plt.figure()
    plt.plot(current_year['previous_fantasy_points'], current_year['fantasy_points/game'], 'o')
    plt.xlabel('previous year fantasy points')
    plt.ylabel('current year fantasy points')
    for i, txt in enumerate(current_year['name']):
        plt.annotate(txt, (current_year['previous_fantasy_points'][i], current_year['fantasy_points/game'][i]))
    plt.show()

    return reg.score(X,y), reg.coef_, reg.intercept_


def YoY_pass_attempts(current_year, previous_year):
    qb_names = previous_year['name']
    current_year = current_year[current_year['name'].isin(qb_names)]
    previous_year = previous_year[previous_year['name'].isin(qb_2020['name'])]
    previous_year['previous_pass_attempts'] = previous_year['attempts']
    current_year = current_year[['name', 'attempts']]
    previous_year = previous_year[['name', 'previous_pass_attempts']]
    current_year = current_year.merge(previous_year, how='left', on='name')
    X = current_year[ 'previous_pass_attempts'].to_numpy().reshape((-1,1))
    y = current_year['attempts']
    reg = LinearRegression().fit(X,y)
    print(reg.score(X,y))
    plt.figure()
    plt.plot(current_year['previous_pass_attempts'], current_year['attempts'], 'o')
    plt.xlabel('previous year pass attempts')
    plt.ylabel('current year pass attempts')
    for i, txt in enumerate(current_year['name']):
        plt.annotate(txt, (current_year['previous_pass_attempts'][i], current_year['attempts'][i]))
    plt.show()

    return reg.score(X,y), reg.coef_, reg.intercept_


reg_score, reg_coef, reg_intercept = YoY_pass_attempts(qb_2020, qb_2019)



"""
plt.figure()
plt.figure()
plt.plot(qb_2019["fantasy_points"], qb_2020["fantasy_points"], 'o')
plt.xlabel('2019 fantasy points')
plt.ylabel('2020 fantasy points')
plt.show()
"""
