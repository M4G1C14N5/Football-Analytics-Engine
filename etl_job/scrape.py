import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Helper Functions ---

def init_driver():
    print("Initializing driver...", flush=True)
    """Initializes and returns a Selenium Driver with anti-detection options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(180) # Prevent timeouts on slow pages
    return driver

def get_data_from_txt(file_path):
    print("Reading data from txt file...", flush=True)
    """Reads HTML content from a file and returns a dataframe."""
    file_path = Path(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        raise ValueError("No table found in the HTML content")
    
    thead = table.find('thead')
    if thead:
        column_headers = thead.find_all('th')
        column_names = [th.get('aria-label', th.text.strip()) for th in column_headers]
    else:
        column_names = []
    
    tbody = table.find('tbody')
    data = []
    if tbody:
        for row in tbody.find_all('tr'):
            row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
            data.append(row_data)
    
    df = pd.DataFrame(data)
    
    # Fix column mismatches
    if len(df.columns) > len(column_names):
        df = df.iloc[:, :len(column_names)]
    elif len(df.columns) < len(column_names):
        column_names = column_names[:len(df.columns)]
    
    df.columns = column_names
    print("Data read successfully...", flush=True)
    return df

# --- Scraping Functions (Now accepting 'driver' as an argument) ---

def get_squad_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping squad stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/stats/squads/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_teams_standard_for")))
            table_div = driver.find_element(By.ID, "div_stats_teams_standard_for")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"squad_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved squad stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_squad_wages(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping squad wages...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/wages/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_squad_wages")))
            table_div = driver.find_element(By.ID, "div_squad_wages")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"squad_wages_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved squad wages for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_standard_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping standard stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/stats/players/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_standard")))
            table_div = driver.find_element(By.ID, "div_stats_standard")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"standard_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved standard stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_defensive_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping defensive stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/defense/players/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_defense")))
            table_div = driver.find_element(By.ID, "div_stats_defense")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"defensive_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved defensive stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_passing_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping passing stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/passing/players/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_passing")))
            table_div = driver.find_element(By.ID, "div_stats_passing")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"passing_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved passing stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_shooting_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping shooting stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)

    for season in seasons:
        url = f"https://fbref.com/en/comps/Big5/{season}/shooting/players/{season}-Big-5-European-Leagues-Stats"
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_shooting")))
            table_div = driver.find_element(By.ID, "div_stats_shooting")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"shooting_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved shooting stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

def get_goalkeeping_stats(driver, seasons=None):
    if seasons is None:
        seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    
    print("Scraping goalkeeping stats...", flush=True)
    data_html_dir = Path("data_html")
    data_html_dir.mkdir(parents=True, exist_ok=True)
    base_url = "https://fbref.com/en/comps/Big5/{}/keepers/players/{}-Big-5-European-Leagues-Stats"

    for season in seasons:
        url = base_url.format(season, season)
        print(f"Fetching: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "div_stats_keeper")))
            table_div = driver.find_element(By.ID, "div_stats_keeper")
            html = table_div.get_attribute('outerHTML')
            with open(data_html_dir / f"goalkeeping_stats_{season}_selenium.txt", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved goalkeeping stats for {season}")
        except Exception as e:
            print(f"Could not get table for {season}: {e}")
        time.sleep(5)

# --- Orchestration ---

def get_all_seasons():
    print("get_all_seasons() function called", flush=True)
    
    data_html_dir = Path("data_html")
    if data_html_dir.exists():
        print("✓ Data html directory exists", flush=True)
    else:
        print("✗ Data html directory created", flush=True)
        data_html_dir.mkdir(parents=True, exist_ok=True)

    seasons = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']
    # seasons = ['2023-2024']

    # Initialize Lists
    seasons_squads_stats = []
    seasons_squads_wages = []
    seasons_standard_stats = []
    seasons_defensive_stats = []
    seasons_passing_stats = []
    seasons_shooting_stats = []
    seasons_goalkeeping_stats = []
    
    # Initialize Driver ONCE
    driver = init_driver()
    
    try:
        # 1. Squad Stats
        get_squad_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'squad_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_squads_stats.append(df)
            else:
                print(f"Skipping {season} squad stats (file not found)")
        
        # 2. Wages
        get_squad_wages(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'squad_wages_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_squads_wages.append(df)
        
        # 3. Standard Stats
        get_standard_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'standard_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_standard_stats.append(df)
        
        # 4. Defensive Stats
        get_defensive_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'defensive_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_defensive_stats.append(df)
        
        # 5. Passing Stats
        get_passing_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'passing_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_passing_stats.append(df)
        
        # 6. Shooting Stats
        get_shooting_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'shooting_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_shooting_stats.append(df)
        
        # 7. Goalkeeping Stats
        get_goalkeeping_stats(driver, seasons)
        for season in seasons:
            file_path = data_html_dir / f'goalkeeping_stats_{season}_selenium.txt'
            if file_path.exists():
                df = get_data_from_txt(file_path)
                df["Season"] = season
                seasons_goalkeeping_stats.append(df)

    finally:
        # Ensure driver closes even if scraping fails
        driver.quit()
        print("Driver closed.")
    
    # Concatenate results (check if lists are not empty to avoid errors)
    squads_stats = pd.concat(seasons_squads_stats, ignore_index=True) if seasons_squads_stats else pd.DataFrame()
    squads_wages = pd.concat(seasons_squads_wages, ignore_index=True) if seasons_squads_wages else pd.DataFrame()
    standard_stats = pd.concat(seasons_standard_stats, ignore_index=True) if seasons_standard_stats else pd.DataFrame()
    defensive_stats = pd.concat(seasons_defensive_stats, ignore_index=True) if seasons_defensive_stats else pd.DataFrame()
    passing_stats = pd.concat(seasons_passing_stats, ignore_index=True) if seasons_passing_stats else pd.DataFrame()
    shooting_stats = pd.concat(seasons_shooting_stats, ignore_index=True) if seasons_shooting_stats else pd.DataFrame()
    goalkeeping_stats = pd.concat(seasons_goalkeeping_stats, ignore_index=True) if seasons_goalkeeping_stats else pd.DataFrame()
    
    return squads_stats, squads_wages, standard_stats, defensive_stats, passing_stats, shooting_stats, goalkeeping_stats
