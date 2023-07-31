# %%
import pandas_gbq
import pandas as pd
from google.cloud import bigquery

# %%
def load_bway_data(df,proj_id,dest_table):
    '''
        This is the function that will be called from main.py.
        This will remove any existing data from the BigQuery table for which we are attempting to insert data for a season/week that is already there.
        Then it will load the transformed data into the BigQuery table

        args:
            df: a dataframe containing the transformed data
            proj_id: the Google project id
            dest_table: the destination table to load the data to in BigQuery

        returns:
            None
    '''
    
    # first remove the season/wk data that exists in dest_table in order to not insert duplicated data for the week
    remove_season_weeks_if_exist(df,proj_id,dest_table)

    table_schema = [
        {   'name':'tw_gross', 'type':'NUMERIC'},
        {   'name':'potential_gross', 'type':'NUMERIC'},
        {   'name':'diff_tw_lw_gross', 'type':'NUMERIC'},
        {   'name':'avg_ticket_price', 'type':'NUMERIC'},
        {   'name':'max_ticket_price', 'type':'NUMERIC'}
    ]
    # now load df to dest_table
    load_to_gbq(df,proj_id,dest_table)

# %%
def load_to_gbq(df,proj_id,dest_table,table_schema=None):
    # load df to dest_table
    try:
        result = pandas_gbq.to_gbq(dataframe=df, project_id=proj_id, destination_table = dest_table,table_schema = table_schema,if_exists='append')
    except:
        print("There was an issue loading the data to BigQuery")
        exit(1)
    
    print("The data was loaded successfully!")

# %%
def remove_season_weeks_if_exist(df,proj_id,dest_table):
    # first remove any season/week_num that exist in df from dest_table
    #   - we don't want to upload duplicate data for the same week
    df_season_wks = df[['season', 'week_num']].drop_duplicates()

    condition = ''

    # build the query condition for which rows need to be removed from dest_table
    for index,row in df_season_wks.iterrows():
        if index!=0:
            condition += "or "
        condition += f'''(season='{row['season']}' and week_num={row['week_num']})\n'''

    qry = f'''
        CREATE OR REPLACE TABLE {proj_id}.{dest_table} AS
        SELECT *
        from {proj_id}.{dest_table}
        where not ( {condition} )
    '''

    # set up the client
    client = bigquery.Client()

    # Run the query to remove dest_table rows and get the result
    query_job = client.query(qry)
    return query_job.result()


