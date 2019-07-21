#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 20:37:40 2019

@author: CHHuang
"""

import numpy as np
from scipy import stats
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import nltk
from wordcloud import WordCloud
from textblob import TextBlob

plt.style.use('ggplot')

boxoffice = pd.read_csv('Boxofficemojo.csv') 
# Replace NaN with $0 million
boxoffice.production_budget = boxoffice.production_budget.replace(np.nan,'$0 million')
# Transfer '$100,000' string to '100000' 
boxoffice.production_budget[boxoffice.production_budget.str.find(',')!=-1]=\
    boxoffice.production_budget[boxoffice.production_budget.str.find(',')!=-1]\
    .str[1:].apply(lambda x: x.replace(',',''))
# Transfer '$n million' to 'n000000'
boxoffice.production_budget[boxoffice.production_budget.str.find('million')!=-1] = \
    boxoffice.production_budget[boxoffice.production_budget.str.find('million')!=-1].\
    str[1:].apply(lambda x: float(x.replace('million','').strip())*1e6).apply(str)
# Make the budget number to int
boxoffice.production_budget=boxoffice.production_budget.apply(float).apply(int)
# Many movies before 1990 only released in US, so set worldwide gross = domestic gross
boxoffice.worldwide[(boxoffice.worldwide=='ank') | (boxoffice.worldwide.isnull())] = boxoffice.domestic
boxoffice.worldwide = boxoffice.worldwide.apply(int)
boxoffice = boxoffice.sort_values('worldwide',ascending=False)
# Make sure no space in the "name" string
boxoffice.name = boxoffice.name.str.strip()
# Add a new column to indicate if a movie is series movie
boxoffice['Is_series'] = boxoffice.series!='No'


# Read the csv file
num_budget = pd.read_csv('Thenumbers.csv')
# Make sure no space in the "name" string
num_budget.name = num_budget.name.str.strip()
# Sort num_budget with worldwide gross
num_budget = num_budget.sort_values('worldwide',ascending=False)
# Rename the columns
num_budget.columns = ['domestic','name','production_budget_n','release_year','worldwide']

plt.rcParams.update({'font.size': 12,'figure.figsize':(10,5)})
############################################################################################

# Numbers of Series per year
# Bar chart
""" 
Series_per_year = boxoffice[['release_year','series']].loc[boxoffice.release_year!=2019]
Series_per_year = Series_per_year.loc[Series_per_year.series!='No',:].groupby('release_year')
Series_per_year.count().plot.bar(color='b')
plt.suptitle("Numbers of Series per year")
plt.xlabel('Release Year')
plt.ylabel('Number')
plt.show()
"""
# Scatter chart
Series_per_year = boxoffice[['release_year','series']].loc[boxoffice.release_year!=2019]
Series_per_year = Series_per_year.loc[Series_per_year.series!='No',:].groupby('release_year')
Series_per_year = Series_per_year.count().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.pointplot(x="release_year", y="series", data=Series_per_year,xlim=(1980,2020))
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_major_formatter(ticker.ScalarFormatter(-1982))
plt.suptitle("Numbers of Series per year")
plt.xlabel('Release Year')
plt.ylabel('Number')
plt.show()

############################################################################################

# Box chart that compares the worldwide gross for series and non-series movie
ser_vs_world = boxoffice[['Is_series', 'worldwide']]
ser_vs_world.worldwide = ser_vs_world.worldwide.apply(np.log10)
sns.boxplot(x='Is_series', y='worldwide', data=ser_vs_world)
plt.suptitle("Comparison of worldwide gross")
plt.xlabel('Series Movies')
plt.ylabel('log_10(Worldwide Gross)')
plt.show()

# Make two sample t-test
#print('worldwide gross two sample t-test')
#print(stats.ttest_ind(ser_vs_world[ser_vs_world.Is_series == True].worldwide,\
#                    ser_vs_world[ser_vs_world.Is_series == False].worldwide))
#print(ser_vs_world[ser_vs_world.Is_series == True].shape)
#print(ser_vs_world[ser_vs_world.Is_series != True].shape)

# Histogram that compares the worldwide gross for series and non-series movie
iss = ser_vs_world[ser_vs_world.Is_series == True]
isnos = ser_vs_world[ser_vs_world.Is_series == False]
sns.distplot(iss["worldwide"], kde = True, color="skyblue", label="Series Movies")
sns.distplot(isnos["worldwide"], kde = True, color="red", label="Non-series Movies")
plt.suptitle("Comparison of worldwide gross")
plt.legend()
plt.xlabel('log_10(Worldwide Gross)')
plt.show()

############################################################################################
# Bar chart of number of movies only released in US
domestic_movie = boxoffice.loc[boxoffice.worldwide == boxoffice.domestic].loc[boxoffice.release_year!=2019].groupby('release_year').count()
domestic_movie = domestic_movie.reset_index()
domestic_movie.plot(kind='bar',x='release_year', y='domestic',color = 'g')
plt.xlabel('Release Year')
plt.ylabel('Number of movies only released in US')
plt.show()

# Bar chart of total worldwide gross from 1982 to 2018
# A stacked chart shows the domestic and international gross
w_g2 = boxoffice[['release_year','worldwide','domestic']].loc[boxoffice.release_year!=2019]
w_g2['international']= w_g2.worldwide-w_g2.domestic
w_g2 = w_g2.drop('worldwide',1)
w_g2.groupby(['release_year'])[['international','domestic']].sum().plot(kind='bar', stacked=True)
plt.xlabel('Release Year')
plt.ylabel('Total worldwide gross')
plt.show()

# Histogram that compares the worldwide gross for series and non-series movie those released internaionally
int_movie = boxoffice.loc[boxoffice.worldwide != boxoffice.domestic][['Is_series', 'worldwide']]
int_movie.worldwide = int_movie.worldwide.apply(np.log10)
iss_int = int_movie[int_movie.Is_series == True]
isnos_int = int_movie[int_movie.Is_series == False]
sns.distplot(iss_int["worldwide"], color="skyblue", label="Series Movies")
sns.distplot(isnos_int["worldwide"], color="red", label="Non-series Movies")
plt.suptitle("Comparison of worldwide gross (movies released internaionally)")
plt.legend()
plt.xlabel('log_10(Worldwide Gross)')

# Make two sample t-test
#print(stats.ttest_ind(int_movie[int_movie.Is_series == True].worldwide,\
#                    int_movie[int_movie.Is_series == False].worldwide))


############################################################################################
# To get more budget data. Merge num_budget and boxoffice data frame
# Merged table
name_pb = num_budget[['name','production_budget_n']]
name_pb.name = name_pb.name.str.strip()
# Left join boxoffice and name_pb, then sort the DF by release_year
Merged_df = pd.merge(boxoffice, name_pb, how='left', on ='name').sort_values('release_year',ascending=False)
# There are some NaN at column 'production_budget_n', and the values in that column are change to float type.
# So I use apply(int) to make the values integer.
Merged_df.production_budget_n = Merged_df.production_budget_n.replace(np.nan,0).apply(int)
# If the production_budget in boxoffice is zero, then replace it with the value from num_budget
Merged_df.loc[(Merged_df.production_budget ==0)&(Merged_df.production_budget_n!=0)].production_budget = \
	Merged_df.loc[(Merged_df.production_budget ==0)&(Merged_df.production_budget_n!=0)].production_budget_n
# Drop production_budget_n column
Merged_df = Merged_df.drop('production_budget_n', 1)
# Only retain movies with not zero production_budget 
Merged_df = Merged_df.loc[Merged_df.production_budget != 0]
# Calculate profit
Merged_df['profit'] = (Merged_df.worldwide - Merged_df.production_budget)/Merged_df.production_budget



# Histogram that compares the profit for series and non-series movie those released internaionally
int_profit = Merged_df.loc[Merged_df.worldwide != Merged_df.domestic][['name','Is_series', 'profit','release_year']].sort_values('profit',ascending=False)
int_profit = int_profit.loc[int_profit.profit < 20]
iss_profit = int_profit[int_profit.Is_series == True]
isnos_profit = int_profit[int_profit.Is_series == False]
############################################################################################
# There is a strange bug in this plot, please check test.ipynb for the plot
############################################################################################
sns.distplot(iss_profit["profit"], color="skyblue", label="Series Movies")
sns.distplot(isnos_profit["profit"], color="red", label="Non-series Movies")
plt.legend()
#sns.boxplot(x='Is_series', y='profit', data=int_profit)
plt.xlabel('Profit')
plt.show()
#plt.ylabel('Profit')
#print(iss_profit.profit.agg(['mean','median','std']))
#print(isnos_profit.profit.agg(['mean','median','std']))
# Two sample t-test
#print(stats.ttest_ind(int_profit[int_profit.Is_series == True].profit,\
#                    int_profit[int_profit.Is_series == False].profit))

# Histogram, the profit that the first movie of a moive series made
First_series = Merged_df.loc[(Merged_df.worldwide != Merged_df.domestic) & (Merged_df.series!= 'No')].sort_values('release_year').groupby('series')
a=[]
b=[]
for index, row in First_series:
    a.append(row.loc[row.release_year ==row.release_year.min()].profit)
for i in range(len(a)):
    b+=list(a[i].values)
df1 = pd.DataFrame(b,columns=['first_profit'])
df1 = df1.loc[df1.first_profit < 25]
sns.distplot(df1["first_profit"], color="skyblue", label="Series Movies")
plt.suptitle("Profit that the first movie of a moive series made")
plt.xlabel('Profit')
plt.show()
#print(df1.first_profit.agg(['mean','median','std']))



############################################################################################
# Make dataframe for genre
df_genre = Merged_df.copy()
df_genre.genre = df_genre.genre.str.replace('/','').str.split()
df_genre.index = list(range(df_genre.shape[0]))
df_genre.sort_values('worldwide',ascending=False)
# i keeps tracks of index
index=0
# save [index, genre] in a nested list
list_ = []
for item in df_genre.genre:
    list_.extend(map(lambda x: [index, x], item))
    index += 1
genre = pd.DataFrame(list_, columns=['index', 'genre'])
df_genre = pd.merge(df_genre.drop('genre', axis=1), genre, how='right', left_index=True, right_on='index')
df_genre = df_genre.loc[(df_genre.genre != 'Unknown')]
df_genre.worldwide = df_genre.worldwide.apply(np.log10)

# Bar chart of median profit for different genre
df_genre.groupby(['genre', 'Is_series'])['profit'].median().sort_values(ascending=False).plot.bar(color='b',figsize=[14,5])
plt.suptitle("Median profit for different genre")
plt.ylabel('Median Profit')
plt.show()

# Bar chart of mean budget for different genre
df_genre.groupby(['genre', 'Is_series'])['production_budget'].mean().sort_values(ascending=False).plot.bar(color='b',figsize=[14,5])
plt.suptitle("Mean production budget for different genre")
plt.ylabel('Mean Production_budget')
plt.show()

############################################################################################
#					NLP
############################################################################################
RT = pd.read_csv('Rottentomatoes.csv')
RT.context = RT.context.fillna('')

import re
# Convert all the string to lower cases
RT.context = RT.context.str.lower()
# \S+ means anything that is not an empty space
RT.context = RT.context.apply(lambda x: re.sub('http\S*', '', x))
# \s+ means all empty space (\n, \r, \t)
RT.context = RT.context.apply(lambda x: re.sub('\s+', ' ', x))

# Convert score to int
RT.critic_score = RT.critic_score.str.replace('%','').apply(int)
RT.aud_score = RT.aud_score.str.replace('%','').apply(int)

# Remove any punctuation
RT.context = RT.context.apply(lambda x: re.sub('[^\w\s]', '', x))

# Add some stopwords
from nltk.corpus import stopwords
stop = stopwords.words('english')
stop2 = ['one','movie','film','make','movies','films','time','genre','full  review','makes','way','much','many','good',\
        'review spanish','even','spanish','still','remake','made','take','thats','really','us','never','may'] 
stop += stop2

# Remove stopwords from comment
RT.context = RT.context.apply(lambda x: " ".join(x for x in x.split() if x not in stop))

# Tried to make wordcloud for different genre, but didn't find significant insight
RT_horror = RT[RT.genre.str.find('Horror')!=-1]
RT_romance = RT[RT.genre.str.find('Romance')!=-1]
RT_comedy = RT[RT.genre.str.find('Comedy')!=-1]
RT_aa = RT[RT.genre.str.find('Action & Adventure')!=-1]

wc = WordCloud(background_color="white", max_words=2000, width=800, height=400)
# generate word cloud
wc.generate(' '.join(RT.context))

plt.figure(figsize=(12, 6))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

# Create two dataframes. One only contain the context with fresh review, the other only contain the context with rotten review
fresh_df = RT[RT.fresh_rot == 'fresh']
rotten_df = RT[RT.fresh_rot != 'fresh']

def sentiment_func(x):
    sentiment = TextBlob(x['context'])
    x['polarity'] = sentiment.polarity
    x['subjectivity'] = sentiment.subjectivity
    return x

# polarity plot
fresh = fresh_df.apply(sentiment_func, axis=1)
fresh.plot.scatter('critic_score', 'polarity')
plt.xlabel('Critic score')
plt.show()

rotten = rotten_df.apply(sentiment_func, axis=1)
rotten.plot.scatter('critic_score', 'polarity')
plt.xlabel('Critic score')
plt.show()

# Correlation of score from critics and score from audience
g = sns.lmplot("critic_score", "aud_score", RT)
g.set(ylim=(40, 105),xlim=(40,105))
plt.xlabel('Critic score')
plt.ylabel('Audience score')
plt.show()












