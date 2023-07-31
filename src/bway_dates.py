# %%
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# %%
def generate_week_data():
    tdelta_begin_wk = timedelta(days = -6)
    tdelta_next_week_end_date = timedelta(days = 7)

    season_weeks = [
        ['2017-18',datetime(2017,5, 28),0,53],
        ['2018-19',datetime(2018,6, 3),0,52],
        ['2019-20',datetime(2019,6, 2),0,41],
        ['2020-21',datetime(2020,6, 1),-1,52],
        ['2021-22',datetime(2021,5, 30),10,52],
        ['2022-23',datetime(2022,5, 29),0,52],
        ['2023-24',datetime(2023,5, 28),0,52]
    ]

    week_df_columns = ['season','week_num','week_start_date','week_end_date']
    week_data = []

    for row in season_weeks:
        season = row[0]
        season_start_date_we = row[1]
        num_weeks_offset = row[2]
        week_end_date = season_start_date_we + timedelta(days=7*num_weeks_offset)
        num_weeks = row[3]

        if not(season == '2020-21'): #exclude the 2020-21 season because of Pandemic
            
            for i in range(num_weeks_offset+1,num_weeks+1):
                week_start_date = week_end_date + tdelta_begin_wk
                
                week_data.append([season,i,week_start_date,week_end_date])
    
                week_end_date += tdelta_next_week_end_date
            
    df_week_data = pd.DataFrame(week_data,columns=week_df_columns)

    return df_week_data

# %%
def get_most_recent_week():
    current_datetime = datetime.now()
    df_week_data = generate_week_data()
    df_week_data['current_datetime'] = current_datetime
    df_week_data['time_diff'] = (df_week_data['current_datetime'] - df_week_data['week_end_date'])
    df_week_data_filtered = df_week_data[df_week_data['time_diff'] >= timedelta(days=1)]
    df_sorted = df_week_data_filtered.sort_values(by='time_diff',ascending=True)
    df_sorted = df_sorted.drop(columns=['time_diff','current_datetime'])
    return df_sorted.head(1)

# %%
def get_historical_weeks_from_range(season_start,week_start,season_end,week_end):
    
    df = generate_week_data()
    index_start = df.loc[(df['season'] == season_start) & (df['week_num'] == int(week_start))].index[0]
    index_end = df.loc[(df['season'] == season_end) & (df['week_num'] == int(week_end))].index[0]
    df_week_data_filtered =  df[index_start:index_end+1]
    return df_week_data_filtered


