import os
import sys
import datetime
from time import sleep
import random
import re
import pandas as pd
import src.bway_dates as bway_dates
from src.extract import extract_from_website
from src.transform import transform_data
from src.load import load_bway_data

#### IMPORTANT ####
# Set below two variables based on the names of your GBQ project, Dataset Name and Table Name
###################
proj_id = 'broadway-data-393814'
dest_table = 'broadway_grosses.weekly_grosses'

def main():
    """
    
    This function serves as the entrypoint to run an ETL process.
    The data being extracted is related to Broadway attendance/grosses
    It will scrape data from a website, transform/clean it, and load it into a BigQuery table
        

    Args:
        When running the program, you can optionally enter a range of weeks to pull:
        [season_start] [week_num_start] [season_end] [week_num_end]
        ex. python main.py 2017-18 1 2018-19 52

        If no args are passed, it will attempt to ETL the most recently available week of data

    Returns:
        None  
    """

    
    base_url = 'https://playbill.com/grosses?week='

    weeks_to_run = pd.DataFrame()

    if len(sys.argv)<=1:
        # defaults to running the script for the most recent full week
        weeks_to_run = bway_dates.get_most_recent_week()
    else:
        # check to make sure that we have proper args for season_start, week_start, season_end, week_end
        # should be formatted, eg: 2017-18 1 2022-23 52

        # helper function to check proper formatting of season
        def check_season_format(season):
            pattern = r'^\d{4}-\d{2}$'
            match = re.match(pattern, season)
            return match is not None
        
        # helper function to check proper formatting of week number
        def check_week_num_format(week_num):
            pattern = r'^(?:[1-9]|[1-4][0-9]|5[0-3])$'
            match = re.match(pattern, week_num)
            return match is not None
        
        # make sure all args are there and formatted properly, else throw an error and exit
        try:
            season_start = sys.argv[1]
            if not check_season_format(season_start):
                print("season_start format is incorrect.  Try dddd-dd")
                sys.exit(1)

            week_num_start = sys.argv[2]
            if not check_week_num_format(week_num_start):
                print("week_num_start format is incorrect. Use number between 1 and 53")
                sys.exit(1)

            season_end = sys.argv[3]
            if not check_season_format(season_end):
                print("season_end format is incorrect.  Try dddd-dd")
                sys.exit(1)

            week_num_end = sys.argv[4]
            if not check_week_num_format(week_num_end):
                print("week_num_end format is incorrect. Use number between 1 and 53")
                sys.exit(1)

            weeks_to_run = bway_dates.get_historical_weeks_from_range(season_start,week_num_start,season_end,week_num_end)
        except IndexError:
            print("Missing argument")
            sys.exit(1)

        

    df_to_load = pd.DataFrame()

    # iterate over weeks_to_run, doing the extract and transform, and appending into df_to_load
    for ix, wk_row in weeks_to_run.iterrows():
        time_to_sleep = random.uniform(1,3)
        print(f'sleeping for {time_to_sleep} seconds')
        sleep(time_to_sleep)
        
        # put the week ending date in yyyy-mm-dd string format
        week_end_date_str = datetime.datetime.strftime(wk_row['week_end_date'],'%Y-%m-%d')
        
        # extract data from website
        extracted_data = extract_from_website(base_url,week_end_date_str)
        
        # transform data
        df_transformed = transform_data(extracted_data)
        
        # append data to df_to_load, for bulk upload to BigQuery hereafter
        df_to_load = pd.concat([df_to_load,df_transformed],ignore_index=True)

    # load the final data into the BigQuery table
    load_result = load_bway_data(df_to_load,proj_id,dest_table)

if __name__ == "__main__":
    main()