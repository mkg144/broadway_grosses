# %%
import pandas as pd
from datetime import datetime, timedelta
import os
import requests

# %%
def extract_from_website(base_url,report_weekend_date):
    '''
        This is the function that will be called from main.py.
        This function will get the response text from requesting the provided base_url

        args:
            base_url: the url for the website
            report_weekend_date: the week ending date for the report (as a string yyyy-mm-dd) that will be appended to the base_url as a parameter

        returns:
            the response text if there is a valid response 
    '''
    
    # form the full URL to the weekly report
    url = f'{base_url}{report_weekend_date}'
    
    print(url)
    
    # request the URL
    response = requests.get(url)
    
    # check if good response, and if so, return the response text
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch the webpage.")
        return False