from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import mysql.connector
import pandas as pd
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException,TimeoutException
import pickle
def get_new_status_from_external_source(submission,driver):
    search_box = driver.find_element(By.ID,"searchInput")  # Replace "q" with the actual attribute value of the search box

    search_box.clear()
    search_text = str(submission)
    search_box.send_keys(search_text)

    # Submit the search by pressing the Enter key
    search_box.send_keys(Keys.RETURN)

    if driver.current_url=='https://www.psacard.com/errors?aspxerrorpath=/myaccount/myorder':
        return 'ARRIVED'
    else:
        try:
            wait = WebDriverWait(driver, 10)

            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bar-purple')))

            element = driver.find_element(By.ID,'order-progress-bar')
            e2=element.find_element(By.CLASS_NAME,'bar-purple')
            return e2.text
        except TimeoutException:
            return 'SHIPPED'
    
def main():
    driver = webdriver.Chrome()
    url = "https://www.psacard.com"
    driver.get(url)

    driver.delete_all_cookies()

    path='cookies.pkl'
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    url = "https://www.psacard.com/myaccount/myorders"
    driver.get(url)
    time.sleep(3)
    db_config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'psa'
    }

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT submission, status FROM orders WHERE status != 'SHIPPED'")
    orders = cursor.fetchall()

    for submission, status in orders:
        # Simulate getting new status from external source (replace with your logic)
        new_status = get_new_status_from_external_source(submission,driver)
        driver.back()
        if new_status != status:
            # Update the status in the database
            update_query = "UPDATE orders SET status = %s WHERE submission = %s"
            update_values = (new_status, submission)
            cursor.execute(update_query, update_values)
            connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

if __name__ == '__main__':
    main()




    