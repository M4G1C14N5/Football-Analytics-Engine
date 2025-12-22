# First we'll import all the libraries we need 


import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Now we'll define the functions we need to scrape the data

# debug_response() prints detailed information about a response to check for bot detection
def debug_response(response, season=None):
    """Debug function to check if a website is detecting automation"""
    print(f"\n=== DEBUG INFO{' for ' + season if season else ''} ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response URL: {response.url}")
    
    print(f"\nResponse Headers (relevant):")
    for key, value in response.headers.items():
        if any(keyword in key.lower() for keyword in ['server', 'cloudflare', 'cf-', 'x-', 'set-cookie', 'content-type']):
            print(f"  {key}: {value}")
    
    if response.status_code == 403:
        print(f"\n⚠️  403 Forbidden Response")
        print(f"Response Content (first 1000 chars):")
        print(response.text[:1000])
        
        # Check for common bot detection indicators
        content_lower = response.text.lower()
        if 'cloudflare' in content_lower or 'challenge' in content_lower:
            print("\n⚠️  Cloudflare challenge detected!")
        if 'captcha' in content_lower:
            print("⚠️  CAPTCHA detected!")
        if 'access denied' in content_lower or 'forbidden' in content_lower:
            print("⚠️  Access denied message found!")
        if 'bot' in content_lower or 'automated' in content_lower:
            print("⚠️  Bot detection message found!")
    
    print("=" * 50)

# get_data_from_txt() takes a file path, reads the HTML content, and returns a dataframe
def get_data_from_txt(file_path):
    # Read the HTML content from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table
    table = soup.find('table')
    
    if not table:
        raise ValueError("No table found in the HTML content")
    
    # Extract column names from thead
    thead = table.find('thead')
    if thead:
        column_headers = thead.find_all('th')
        column_names = [th.get('aria-label', th.text.strip()) for th in column_headers]
    else:
        column_names = []
    
    # Extract data from tbody
    tbody = table.find('tbody')
    data = []
    if tbody:
        for row in tbody.find_all('tr'):
            row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
            data.append(row_data)
    
    # Create dataframe
    df = pd.DataFrame(data)
    
    # Assign column names, truncating or padding as necessary
    if len(df.columns) > len(column_names):
        # If there are more columns in the data than names, use the first len(column_names) columns
        df = df.iloc[:, :len(column_names)]
    elif len(df.columns) < len(column_names):
        # If there are fewer columns in the data than names, truncate the column names
        column_names = column_names[:len(df.columns)]
    
    df.columns = column_names
    
    return df



# get_squad_stats() scrapes fbref link html for standard squad stats, puts it in txt file, and returns txt file address

def get_squad_stats():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    # 🧢 Pretend to be a real Chrome browser
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}
    
    base_url = "https://fbref.com/en/comps/Big5/{}/stats/squads/{}-Big-5-European-Leagues-Stats"
    seasons = ["2022-2023"]  # Start small to test

    for season in seasons:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers=headers)
            debug_response(response, season)  # Debug the response
            response.raise_for_status()  # Raise error for 403s or other HTTP issues

            soup = BeautifulSoup(response.content, 'html.parser')
            table_div = soup.find('div', id='div_stats_teams_standard_for')
            
            if table_div:
                with open(f'data_html/squad_stats_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved squad stats for {season}")
            else:
                print(f"Table div not found for {season}")
            
            time.sleep(random.uniform(5, 10))  # 💤 Nap time

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")
            
    print("✅ All seasons processed")


# get_squad_wages() scrapes fbref link html for squad wages, puts it in txt file, and returns txt file address

def get_squad_wages():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    base_url = "https://fbref.com/en/comps/Big5/{}/wages/{}-Big-5-European-Leagues-Stats"
    seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    for season in seasons:
        #if season == "2023-2024":
           # url = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
       # else:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div containing the table
            table_div = soup.find('div', id='div_squad_wages')
            
            if table_div:
                # Save the HTML content of the div to a file
                with open(f'data_html/squad_wages_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved squad wages for {season}")
            else:
                print(f"Table div not found for {season}")
            
            # Introduce a random delay between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")

    print("All seasons processed")
    return f'data_html/squad_wages_{season}.txt'



# get_standard_stats() scrapes fbref link html for defensive stats, puts it in txt file, and returns txt file address

def get_standard_stats():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    base_url = "https://fbref.com/en/comps/Big5/{}/stats/players/{}-Big-5-European-Leagues-Stats"
    seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    for season in seasons:
        #if season == "2023-2024":
            #url = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
        #else:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div containing the table
            table_div = soup.find('div', id='div_stats_standard')
            
            if table_div:
                # Save the HTML content of the div to a file
                with open(f'data_html/standard_stats_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved standard stats for {season}")
            else:
                print(f"Table div not found for {season}")
            
            # Introduce a random delay between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")

    print("All seasons processed")
    return f'data_html/standard_stats_{season}.txt'
    

# get_defensive_stats() scrapes fbref link html for defensive stats, puts it in txt file, and returns txt file address

def get_defensive_stats():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    base_url = "https://fbref.com/en/comps/Big5/{}/defense/players/{}-Big-5-European-Leagues-Stats"
    seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    for season in seasons:
        #if season == "2023-2024":
           # url = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
       # /else:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div containing the table
            table_div = soup.find('div', id='div_stats_defense')
            
            if table_div:
                # Save the HTML content of the div to a file
                with open(f'data_html/defensive_stats_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved defensive stats for {season}")
            else:
                print(f"Table div not found for {season}")
            
            # Introduce a random delay between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")

    print("All seasons processed")
    return f'data_html/defensive_stats_{season}.txt'

# get_passing_stats() scrapes fbref link html for defensive stats, puts it in txt file, and returns txt file address

def get_passing_stats():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    base_url = "https://fbref.com/en/comps/Big5/{}/passing/players/{}-Big-5-European-Leagues-Stats"
    seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    for season in seasons:
        #if season == "2023-2024":
           # url = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
       # else:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div containing the table
            table_div = soup.find('div', id='div_stats_passing')
            
            if table_div:
                # Save the HTML content of the div to a file
                with open(f'data_html/passing_stats_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved passing stats for {season}")
            else:
                print(f"Table div not found for {season}")
            
            # Introduce a random delay between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")

    print("All seasons processed")
    return f'data_html/passing_stats_{season}.txt'

# Example usage: only run this for shooting stats
#get_shooting_stats()  # Or add more seasons as needed

def get_shooting_stats(seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]

    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    os.makedirs("data_html", exist_ok=True)

    for season in seasons:
        url = f"https://fbref.com/en/comps/Big5/{season}/shooting/players/{season}-Big-5-European-Leagues-Stats"
        print(f"Fetching: {url}")
        driver.get(url)
        try:
            # Wait up to 20 seconds for the table div to appear
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "div_stats_shooting"))
            )
            table_div = driver.find_element(By.ID, "div_stats_shooting")
            html = table_div.get_attribute('outerHTML')
            with open(f"data_html/shooting_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved shooting stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        # Space out requests to avoid being flagged
        time.sleep(8)

    driver.quit()
    print("All requested seasons processed.")



# get_goalkeeping_stats() scrapes fbref link html for goalkeeper stats, puts it in txt file, and returns txt file address

def get_goalkeeping_stats():
    session = requests.Session()
    
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    base_url = "https://fbref.com/en/comps/Big5/{}/keepers/players/{}-Big-5-European-Leagues-Stats"
    seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    for season in seasons:
        #if season == "2023-2024":
           # url = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
       # else:
        url = base_url.format(season, season)
        
        try:
            response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div containing the table
            table_div = soup.find('div', id='div_stats_keeper')
            
            if table_div:
                # Save the HTML content of the div to a file
                with open(f'data_html/goalkeeping_stats_{season}.txt', 'w', encoding='utf-8') as file:
                    file.write(str(table_div))
                print(f"Saved goalkeeping stats for {season}")
            else:
                print(f"Table div not found for {season}")
            
            # Introduce a random delay between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for season {season}: {e}")

    print("All seasons processed")
    return f'data_html/goalkeeping_stats_{season}.txt'



# get_all_seasons() loops through all the txt files, extracts the data, and adds it to a dataframe for all seasons

def get_all_seasons():
    # List of seasons to loop through
    seasons = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']
    # dataframes to store squad stats, and wages
    seasons_squads_stats = []
    seasons_shooting_stats = []
    seasons_squads_wages = []
    seasons_standard_stats = []
    seasons_defensive_stats = []
    seasons_passing_stats = []
    seasons_goalkeeping_stats = []
    
    # Getting squads stats data
    get_squad_stats()
    for season in seasons:
        file_path = f'data_html/squad_stats_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_squads_stats.append(df)
        
    # Getting squad wages data
    get_squad_wages()
    for season in seasons:
        file_path = f'data_html/squad_wages_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_squads_wages.append(df)
    
    # Getting standard player stats
    get_standard_stats()
    for season in seasons:
        file_path = f'data_html/standard_stats_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_standard_stats.append(df)
        
    # Getting defensive player stats
    get_defensive_stats()
    for season in seasons:
        file_path = f'data_html/defensive_stats_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_defensive_stats.append(df)
    
    # Getting passing player stats
    get_passing_stats()
    for season in seasons:
        file_path = f'data_html/passing_stats_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_passing_stats.append(df)
        
    get_shooting_stats()
    for season in seasons:
        file_path = f'data_html/shooting_stats_{season}_selenium.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_shooting_stats.append(df)
        
    # Getting goalkeeping player stats
    get_goalkeeping_stats()
    for season in seasons:
        file_path = f'data_html/goalkeeping_stats_{season}.txt'
        df = get_data_from_txt(file_path)
        df["Season"] = season
        seasons_goalkeeping_stats.append(df)
    
    
    squads_stats = pd.concat(seasons_squads_stats, ignore_index=True)
    squads_wages = pd.concat(seasons_squads_wages, ignore_index=True)
    standard_stats = pd.concat(seasons_standard_stats, ignore_index=True)
    defensive_stats = pd.concat(seasons_defensive_stats, ignore_index=True)
    passing_stats = pd.concat(seasons_passing_stats, ignore_index=True)
    shooting_stats = pd.concat(seasons_shooting_stats, ignore_index=True)
    goalkeeping_stats = pd.concat(seasons_goalkeeping_stats, ignore_index=True)
    
    return squads_stats, squads_wages, standard_stats, defensive_stats, passing_stats, shooting_stats, goalkeeping_stats


    

