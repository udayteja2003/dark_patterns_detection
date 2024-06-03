import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_cors import CORS  # Import CORS from flask_cors
import mysql.connector

app = Flask(__name__)
CORS(app)

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
def handle_amazon(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        time.sleep(15)
        wait = WebDriverWait(driver, 30)
        countdown_timer = wait.until(EC.visibility_of_element_located((By.ID, 'detailpage-dealBadge-countdown-timer')))
        #temp = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[5]/div[3]/div[1]/div[3]/div/div[1]/div/div/div/form/div/div/div/div/div[4]/div/div[5]/div/div[1]/span')))
        temp = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[@data-csa-c-type="element" and @data-csa-c-content-id="DEXUnifiedCXPDM" and @data-csa-c-delivery-price="FREE" and @data-csa-c-delivery-time="Saturday, 13 January" and @data-csa-c-delivery-cutoff="Order within 33 mins"]')))
        countdown_time = countdown_timer.text
        detected_patterns.append("Detected Countdown Timer: " + countdown_time)
        if temp:
          temp1 = temp.text
          detected_patterns.append("Detected False Urgency Pattern: " + temp1)
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns

def handle_realme(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)
        countdown_day_element = wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[3]/div[2]/div/div[2]/div[1]/div/div/div/div[2]/span')))
               
        if countdown_day_element:
           detected_patterns.append("Detected Countdown Timer ")
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns

def handle_meesho(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increased the wait time
        countdown_timer = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[1]/div[2]/div/span')))
        if countdown_timer:
            countdown_time = countdown_timer.text
            detected_patterns.append("Detected Countdown Timer: " + countdown_time)
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def handle_jiomart(driver,url):
    detected_patterns = []
    try:
        
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
                  detected_patterns.append(f"'{common_pattern}' persists for last three days.")  
            
            
            conn.commit()
            
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def handle_pepperfry(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increased the wait time
        #countdown_timer = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/main/app-vip/div/div[2]/div[2]/div[2]/section/pf-vip-qty-total-price/div/div/div/span' )))
        #countdown_timer2 = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/main/app-vip/div/div[2]/div[2]/div[2]/section/pf-vip-qty-total-price/div/div/div/span')))
        findprice = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/main/app-vip/div/div[2]/div[2]/div[2]/section/div[2]/pf-vip-product-price-coupon/div/div[2]/div[1]/div[2]/div[1]/span[1]')))
        countdown_timer = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/main/app-vip/div/div[2]/div[2]/div[2]/section/pf-vip-qty-total-price/div/div/div/span' )))
        countdown_timer2 = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/app-root/main/app-vip/div/div[2]/div[2]/div[2]/section/div[2]/pf-vip-product-price-coupon/div/div[2]/div[1]/div[2]/div[4]/pf-midnight-countdowner/div/span[2]')))
        if countdown_timer:
            countdown_time = countdown_timer.text
            detected_patterns.append("Detected False Urgency Pattern: " + countdown_time)
        if countdown_timer2:
            countdown_time = countdown_timer2.text
            detected_patterns.append("Detected Countdown Timer: " + countdown_time)
        conn = mysql.connector.connect(
        host='localhost',
        user='Kanyarasi',
        password='password',
        database='dark_patterns'
        )
            # Create a cursor object
        cursor = conn.cursor()
        pattern=countdown_timer.text
        #pattern2=countdown_timer2.text
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
            detected_patterns.append(f" '{common_pattern}' persists for last three days.")  
            
        conn.commit()
    except Exception as e:
        
        
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def handle_koovs(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)
        countdown_day_element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div')))       
        countdown_time = countdown_day_element.text
        detected_patterns.append("Detected False Urgency Pattern: " + countdown_time)
        
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def handle_alibaba(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        countdown_day_element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div/div[3]/div/div[1]')))       
        countdown_time = countdown_day_element.text
        detected_patterns.append("Detected Countdown Timer: " + countdown_time)
        
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def handle_flipkart(driver, url):
    detected_patterns = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increased the wait time
        darkpattern = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[4]' )))
        findprice = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div[1]/div/div')))
        print(darkpattern.text)
        
        if darkpattern:
            
        
           conn = mysql.connector.connect(
           host='Uday',
           user='Kanyarasi',
           password='password',
           database='dark_patterns'
           )
            # Create a cursor object
           cursor = conn.cursor()
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
               detected_patterns.append(f" '{common_pattern}' persists for last three days.")  
            
        conn.commit()
    except Exception as e:
        print("Timeout occurred while waiting for the element:", e)
    return detected_patterns
def check_dark_pattern(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    detected_patterns = []
    try:
            

            print("Checking patterns for URL:", url) 
            # False urgency detection patterns (replace these with your patterns)
            false_urgency_patterns = [
                "Hurry, Only 1 left!",
                "Hurry, Only 2 left!",
                "Hurry, Only 3 left!",
                "Hurry, Only 4 left!",
                "Hurry, Only 5 left!",
                "Hurry, Only 6 left!",
                "Hurry, Only 7 left!",
                "Hurry, Only 8 left!",
                "Hurry, Only 9 left!",
                "Hurry, Only 10 left!",
                "Hurry, Only a few left!",
                "3 left",
                "4 left",
                "Few Left",
                "Hurry! Only 1 Left",
                "Hurry! Only 2 Left",
                "Hurry! Only 3 Left",
                "Hurry! Only 4 Left",
                "Hurry! Only 5 Left",
                "Hurry! Only 6 Left",
                "Hurry! Only 7 Left",
                "Hurry! Only 8 Left",
                "Hurry! Only 9 Left",
                "Only 1 left in stock.",
                "Only 2 left in stock.",
                "if ordered before",
                "Limited stock",
                "in the last",
                "Price dropped by",
                "Only few left",
                # Add your patterns here
            ]
            for pattern in false_urgency_patterns:
                if re.search(pattern, text):
                    detected_patterns.append(f"Detected False Urgency Pattern: {pattern}")
            countdown_day_element = soup.find('span', {'class': 'countdown-day'})
            countdown_day = countdown_day_element.text.strip() if countdown_day_element else None

            if countdown_day:
              detected_patterns.append("Detected Countdown Pattern: "+countdown_day)
            
    except Exception as e:
            print(f"Error occurred while using Beautiful Soup: {e}")

    if "amazon.in" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        #options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_amazon(driver, url))
        driver.quit()
    elif "realme.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        #options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_realme(driver, url))
        driver.quit()
    elif "meesho.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_meesho(driver, url))
        driver.quit()
    elif "jiomart.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        
        detected_patterns.extend(handle_jiomart(driver, url))
        driver.quit()
    elif "pepperfry.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_pepperfry(driver, url))
        driver.quit()
    elif "koovs.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_koovs(driver, url))
        driver.quit()
    elif "alibaba.com" in url:
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_alibaba(driver, url))
        driver.quit()
        
    elif "flipkart.com" in url:
        countdown_pattern = re.compile(r'Republic Day Sale Ends In:\d{1,2}hrs:\d{2}mins:\d{2}secs')  
        countdown_match = countdown_pattern.search(text)
        if countdown_match:
            detected_patterns.append("Detected Countdown Pattern: "+countdown_match)
        CHROMEDRIVER_PATH = r'chromedriver.exe'  # Replace with your actual chromedriver path
        options = Options()
        options.add_argument('--headless')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        detected_patterns.extend(handle_flipkart(driver, url))
        driver.quit()
    

        # Execute the SQL statement
    

        # Commit the transaction
    #conn.commit()
    print("Detected Patterns:", detected_patterns)
    return detected_patterns



@app.route('/', methods=['POST'])
def detect_patterns():
    data = request.get_json()
    url = data.get('url', '')
    
    # Invoke your pattern detection logic
    detected_patterns = check_dark_pattern(url)
    
    return jsonify(detected_patterns=detected_patterns)
if __name__ == '__main__':
    app.run(debug=True)
