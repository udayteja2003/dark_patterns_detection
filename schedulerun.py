import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import re
from bs4 import BeautifulSoup
import schedule

def get_patterns_for_date_and_url(cursor, date, url):
    sql = "SELECT pattern FROM dark_patterns WHERE DATE(time) = %s AND url = %s"
    cursor.execute(sql, (date, url))
    return [row[0] for row in cursor.fetchall()]

# Function to perform analysis on patterns
def analyze_patterns(patterns_for_date):
    # Check if all patterns for the given date are the same
    if len(set(patterns_for_date)) == 1:
        return True, patterns_for_date[0]  # Return True if all patterns are the same, along with the common pattern
    else:
        return False, None
    
# Function to check patterns and store in the database
def check_and_store_patterns():
    urls_to_check = [
        {"url": "https://www.jiomart.com/p/electronics/apple-iphone-13-128-gb-midnight-black/590798548", "function": handle_example1},
        {"url": "https://www.jiomart.com/p/electronics/apple-iphone-13-128-gb-midnight-black/590798548", "function": handle_example1},
        # Add more URLs and their corresponding handler functions here
    ]
    
    detected_patterns = []
    for entry in urls_to_check:
        url = entry["url"]
        detection_function = entry["function"]
        try:
            detected_patterns.extend(detection_function(url))
        except Exception as e:
            print(f"Error occurred while checking {url}: {e}")
    
    # Store detected patterns in the database
    

# Define handler functions for pattern detection for each website
def handle_example1(url):
    detected_patterns = []
    try:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increased the wait time
        darkpattern = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/section/section[2]/div/div/div[2]/div[1]/section[3]/div/div[2]/div/div/span[1]')))
        findprice = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/section/section[2]/div/div/div[2]/div[1]/section[2]/div[1]/div[1]/div[1]/span[1]')))
    
        if darkpattern:
            conn = mysql.connector.connect(
            host='localhost',
            user='Kanyarasi',
            password='password',
            database='dark_patterns'
            )
            # Create a cursor object
            cursor = conn.cursor()
            patterntext = darkpattern.text
            pattern=darkpattern.text
            price=float(findprice.text.replace('₹', '').replace(',', ''))
            current_time = datetime.now()
            sql = "INSERT INTO dark_patterns (url, time, price, pattern) VALUES (%s, %s, %s, %s)"
            values = (url, current_time, price, pattern)
            cursor.execute(sql, values)
            current_date = datetime.now().date()

        # Iterate over the past three days
            for i in range(3):
            # Calculate date for the current iteration
               date_to_check = current_date - timedelta(days=i)
            
            # Retrieve patterns for the current date
               patterns_for_date = get_patterns_for_date_and_url(cursor, date_to_check, url)

            # Perform analysis on patterns for the current date
               is_same_pattern, common_pattern = analyze_patterns(patterns_for_date)

            # If all patterns for three consecutive days are the same, consider it a dark pattern
            if is_same_pattern:
                  detected_patterns.append(f"Dark pattern detected: '{common_pattern}' persists for three consecutive days.")  
            
            
            conn.commit()
            driver.quit()
            
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns


# Function to store detected patterns in the database


# Schedule pattern detection to occur every 2 hours
schedule.every(2).hours.do(check_and_store_patterns)

# Run the scheduler loop indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)
