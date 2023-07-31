# ETL for Broadway Grosses

## Description

ETL for Broadway Grosses is a program to extract data from a website containing weekly information on Broadway grosses and attendances, clean and transform the data, and load it into a Google BigQuery table.

Also included in here is an analysis.ipynb.
Currently empty, but some analysis to come on broadway grosses/attendance!

## Table of Contents

- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [Installation](#installation)
- [Usage](#usage)

## Prerequisites

1. A Docker Host
2. A Google Cloud account:
   - Create a project
   - Set up billing for the project
   - Create a service account for the project and download the .json file to your local machine or wherever the Docker host is set up
    

## Authentication

In order to use Google Cloud resources, we need to make sure the app is authenticating with Google.  There are several different ways to do this... I won't explain them all here. 

The method I will use to be able to run this app in Docker is to create a volume mount at runtime to mount my gcp_secret_key.json file to /app/gcp_secret_key.json.  This allows me to access files from my Windows host from within the container.

## Installation

1. Clone the repository:
   git clone https://github.com/mkg144/broadway_grosses.git
   cd broadway_grosses

2. Create a table in BigQuery within the project you set up using below DDL:
   CREATE TABLE `your_project_id.your_dataset_name.your_table_name`
   (
      show_name STRING,
      venue_name STRING,
      season STRING,
      week_num INT64,
      week_start_date DATE,
      week_end_date DATE,
      tw_gross NUMERIC,
      potential_gross NUMERIC,
      diff_tw_lw_gross NUMERIC,
      avg_ticket_price NUMERIC,
      max_ticket_price NUMERIC,
      seats_sold INT64,
      seats_in_theater INT64,
      performances INT64,
      preview_performances INT64,
      pct_capacity FLOAT64,
      diff_tw_lw_pct_capacity FLOAT64
   );

3. Edit the variables **proj_id** and **dest_table** in the file main.py.  This should be changed to use the names of your Google Cloud Project ID, Dataset, and Table names.

## Usage
1. Build the Docker image (if not already built)
docker build -t broadway_grosses_image .

2. Run the ETL (choose 1 of the 2 methods)

### Method 1:
*Without any args on main.py* 
*(will attempt to ETL most recent week's data from website)*

docker run --rm --name \[name_for_the_container\] -v /path/to/local/gcp_secret_key.json:/app/gcp_secret_key.json \[name_for_the_image\] python main.py

**FOR EXAMPLE:**

docker run --rm --name broadway_grosses_container -v C:\Users\Michael\credentials\gcp_secret_key.json:/app/gcp_secret_key.json broadway_grosses_image python main.py

### Method 2:
*With args on main.py for season_start week_num_start season_end week_num_end*
*(ETL's all weeks within that range based on B'way week schedules in a season)*

docker run --rm --name \[name_for_the_container\] -v /path/to/local/gcp_secret_key.json:/app/gcp_secret_key.json \[name_for_the_image\] python main.py \[season_start\] \[week_num_start\] \[season_end\] \[week_num_end\]

**FOR EXAMPLE:**

docker run --rm --name broadway_grosses_container -v C:\Users\Michael\credentials\gcp_secret_key.json:/app/gcp_secret_key.json broadway_grosses_image python main.py 2017-18 1 2018-19 52

3. Interact with the analysis notebook
*The analysis.ipynb file exists but there's no analysis in it yet*

*For this, we will run the Docker container in interactive mode*

### Step 1: Run the container in interactive mode
docker run -it -p 8888:8888 --name \[name_for_the_container\] -v /path/to/local/gcp_secret_key.json:/app/gcp_secret_key.json:/app/gcp_secret_key.json \[name_for_the_image\] bash

**FOR EXAMPLE:**

docker run -it -p 8888:8888 --name broadway_grosses_container -v C:\Users\Michael\credentials\gcp_secret_key.json:/app/gcp_secret_key.json broadway_grosses_image bash

### Step 2: In interactive mode, start Jupyter Notebook server
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

### Step 3: Copy/Paste the URL provided into your web browser to access the notebook interface.  It should look something like:
http://127.0.0.1:8888/tree?token=the_generated_token