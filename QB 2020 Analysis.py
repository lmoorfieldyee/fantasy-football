import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

URL = "https://www.pro-football-reference.com/years/2020/passing.htm"
#read in html tables which is stored as a list in all_tables
all_tables = pd.read_html(URL)

#selecting out the relevant table from our list
qb_df = all_tables[0]

#dropping column names which are inputted periodically into the dataset
qb_df = qb_df[qb_df['Rk']!='Rk']

#subsetting out columns that I want to keep in my df
cols_to_keep = ['Rk', 'Player', 'Tm', 'Age', 'Pos', 'G', 'GS', 'Cmp', 'Att',
       'Cmp%', 'Yds', 'TD', 'TD%', 'Int', 'Int%', 'Y/A',
       'Y/C', 'Y/G']
qb_df = qb_df[cols_to_keep]

#renaming columns to more readable names
col_names = {'Rk':'qb rank', 'Player':'name', 'Tm':'team', 'Age':'age', 'Pos':'position',
            'G':'games played', 'GS':'games started', 'Cmp':'completions', 'Att':'attempts',
       'Cmp%':'completion percent', 'Yds':'yards gained', 'TD':'td', 'TD%':'td percent',
       'Int':'int', 'Int%':'int percent', 'Y/A':'yards per pass attempt',
       'Y/C':'yards per completion', 'Y/G':'yards per game'}
qb_df.rename(columns=col_names, inplace=True)

#converting column data to the correct class for analysis
convert_col_int = ['age', 'games played',
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
URL = "https://www.pro-football-reference.com/years/2020/rushing.htm"
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
cols_to_keep = ['Player', 'Age', 'Pos', 'G', 'GS', 'Att',
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
qb_starters['name'].replace('\+', '', regex=True, inplace=True)

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

#calculating the average passes thrown per game for all nfl quarterbacks in the 2020 season
avg_passes_thrown = [qb_starters['pass attempts/game'].mean()] * len(qb_starters)

#sorting data by fantasy points scored
qb_starters.sort_values('fantasy_points/game', ascending=False, inplace=True)
print(len(qb_starters))
print(qb_starters.head())

#splitting out qbs based on their fantasy football positions
top_10 = qb_starters.iloc[0:10][['name', 'fantasy_points/game', 'pass attempts/game',
                                'rush yards per game']]
avg_qbs = top_10 = qb_starters.iloc[10:20][['name', 'fantasy_points/game', 'pass attempts/game',
                                'rush yards per game']]
print(top_10)
print(avg_qbs)

#plotting pass attempts vs fantasy points & rushing yards vs fantasy points to visualize any relationships
x = qb_starters['pass attempts/game']
y = qb_starters['fantasy_points/game']
n = qb_starters['name'].replace('.* ', '', regex=True)

plt.figure()
plt.scatter(n, y)
plt.xticks(rotation=45)
plt.show()

plt.figure()
plt.scatter(x, y)
for i, txt in enumerate(n):
    plt.annotate(txt, (x[i], y[i]))
plt.xlabel('Pass Attempts per Game')
plt.ylabel('Fantasy Points per Game')
plt.title('2020 QB Pass Attempts vs \n Fantasy Football Points')
plt.show()


x = qb_starters['rush yards per game']
y = qb_starters['fantasy_points/game']
n = qb_starters['name']

plt.figure()
plt.scatter(x, y)
for i, txt in enumerate(n):
    plt.annotate(txt, (x[i], y[i]))
plt.xlabel('Rush Yards per Game')
plt.ylabel('Fantasy Points per Game')
plt.title('2020 QB Rush Yards vs \n Fantasy Football Points')
plt.show()


#print(qb_starters)

#print(qb_df.dtypes)
#print(qb_df.columns)
#print(qb_df[qb_df['Rk']=='Rk'])
#print(qb_df['Rk'].unique)
