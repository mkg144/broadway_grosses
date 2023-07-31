# %%
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import requests
import src.bway_dates as bway_dates
from bs4 import BeautifulSoup
from decimal import Decimal

# %%
def transform_data(html_content):
    '''
        This is the function that will be called from main.py.

        This function will clean and transform the response text and return a dataframe.

        args:
            html_content: the response text from the URL request
    '''
    
    
    # get the html text into a dataframe
    df = html_content_to_df(html_content)

    # clean our data within the dataframe
    df_clean = clean_data_in_df(df)

    # generate our calendar of Broadway weeks
    df_week_data = bway_dates.generate_week_data()

    # merge our dataframe with the week metadata
    df_final = merge_df_with_week_metadata(df_clean,df_week_data)

    return df_final


# %%
def html_content_to_df(html_content):
    '''
        This function parses the html_content using BeautifulSoup

        args:
            html_content: the response text

        returns:
            a dataframe containing the parsed content
    '''
    
    soup = BeautifulSoup(html_content, 'html5lib') # oddly, html.parser was not finding the header row tr tag of the table

    data = []

    if soup: # make sure there's content to process
        # get the report week ending date
        try:
            report_we_date = soup.find(id='vault-search-results-sort-select').find('option', selected=True).text
        except:
            # If there is no selected=True attribute it's actually indicating that the week we're looking for isn't available and it loaded a different page on the site
            print("The week of data is not yet available. Try again later, or use additional arguments to pull historical data")
            sys.exit(1)
        report_we_date_dt = datetime.strptime(report_we_date,'%Y-%m-%d')

        # get the week number
        weeknum = soup.find('div',class_='week-count').find('span').text

        # find the table element on the webpage
        table = soup.find('div', class_='vault-grosses-result').find('table')

        # find all of the rows within the html table
        rows = table.find_all('tr')

        # iterate over all of the table rows including within the table header
        for row in rows:

            row_data = []
            cells = row.find_all(['th', 'td'])
            
            # iterate over all of the cells within the row and fetch the respective cell value
            for cell in cells:
                # if it is a column header
                if cell.name=='th':
                    row_data.append(cell.a.text.strip())

                    if(cell.find('span',class_='subtext')):
                        row_data.append(cell.find('span',class_='subtext').text.strip())
                    else:
                        row_data.append(None)
                # it is not a column header
                else:
                    if(cell.find('span',class_='data-value')):
                        row_data.append(cell.find('span',class_='data-value').text.strip())
                    else:
                        row_data.append(None)

                    if(cell.find('span',class_='subtext')):
                        row_data.append(cell.find('span',class_='subtext').text.strip())
                    else:
                        row_data.append(None)
            
            # append the row data
            data.append(row_data)

        # create a dataframe from the processed data
        df = pd.DataFrame(data[1:], columns=data[0])

        # add an additional column in the dataframe for the report week ending date
        df['week_end_date'] = report_we_date_dt
        return df

    else:
        print("there is no soup")
        return False


# %%
def clean_data_in_df(df_to_clean):
    '''
        This function cleans the data in df_to_clean.
        It drops NA columns, fixes/adds column names, fixes datatypes, and handles missing data

        args:
            df_to_clean: the dataframe with the data that has been parsed from the response text

        returns:
            a cleaned up dataframe
    '''
    
    df = df_to_clean.copy()
    
    # drop NA columns
    df = df.dropna(axis=1, how='all')

    # add a column name for the Venue
    df.columns.values[1] = 'venue_name'

    # rename columns to what they are in the db table
    df.rename(columns={
        'Show' : 'show_name',
        'This Week Gross' : 'tw_gross',
        'Potential Gross' : 'potential_gross',
        'Diff $' : 'diff_tw_lw_gross',
        'Avg Ticket' : 'avg_ticket_price',
        'Top Ticket' : 'max_ticket_price',
        'Seats Sold' : 'seats_sold',
        'Seats in Theatre' : 'seats_in_theater',
        'Perfs' : 'performances',
        'Previews' : 'preview_performances',
        f'% Cap' : 'pct_capacity',
        f'Diff % cap' : 'diff_tw_lw_pct_capacity'
    },inplace=True)

    # convert the currency strings to floats
    def convert_currency_to_decimal(value):
        # Check if the value is a string and contains a dollar sign
        if isinstance(value, str) and '$' in value:
            # Remove dollar sign and comma, and convert to float
            return Decimal(value.replace(',', '').replace('$', ''))
        return Decimal('NaN')

    currency_columns_to_convert = ['tw_gross','potential_gross','diff_tw_lw_gross','avg_ticket_price','max_ticket_price']
    df[currency_columns_to_convert] = df[currency_columns_to_convert].applymap(convert_currency_to_decimal)

    # convert string numbers to integers
    def convert_str_numbers_to_numbers(value):
        converted_value = value
        if isinstance(value, str):
            if ',' in value:
                converted_value = converted_value.replace(',','')
            return int(converted_value)
        return None

    number_columns_to_convert = ['seats_sold','seats_in_theater','performances','preview_performances']
    df[number_columns_to_convert] = df[number_columns_to_convert].applymap(convert_str_numbers_to_numbers)

    # convert percent values to floats
    def convert_pct_to_float(value):
        if isinstance(value, str) and '%' in value:
            return float(value.replace('%', '')) / 100
        return None

    pct_columns_to_convert = ['pct_capacity','diff_tw_lw_pct_capacity']
    df[pct_columns_to_convert] = df[pct_columns_to_convert].applymap(convert_pct_to_float)

    return df

# %%
def merge_df_with_week_metadata(df,df_week_data):
    '''
        This function merges the cleaned up df with our Broadway week metadata

        args:
            df: the cleaned up data
            df_week_data: the Broadway week metadata

        returns:
            the final dataframe that will eventually get loaded into the BigQuery table
    '''
    
    # merge the dataframes to add on the additional metadata
    df_merged = pd.merge(df,df_week_data,how='left',on='week_end_date')

    # make a dataframe with only the necessary columns in the proper order required for loading to BigQuery table
    df_final = df_merged[[
        'show_name',
        'venue_name',
        'season',
        'week_num',
        'week_start_date',
        'week_end_date',
        'tw_gross',
        'potential_gross',
        'diff_tw_lw_gross',
        'avg_ticket_price',
        'max_ticket_price',
        'seats_sold',
        'seats_in_theater',
        'performances',
        'preview_performances',
        'pct_capacity',
        'diff_tw_lw_pct_capacity'
    ]]

    return df_final



