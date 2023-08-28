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
import pickle
def is_scrolled_to_top(driver):
    # Execute JavaScript to get the scroll position
    scroll_position = driver.execute_script("return window.scrollY;")
    return scroll_position == 0  # Returns True if scrolled to the top


def main():
    db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'psa'
}
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
        element_locator = (By.XPATH, '//*[@id="tableOrders_paginate"]/span/span')

        # Wait for the element to load
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located(element_locator))
        print(element.text)
        pages=int(element.text.replace('/ ',''))
        print(pages)
        rows = []
        headers = []
        for i in range(1,pages+1):
            if i>1:
                select_locator = (By.XPATH, '//*[@id="tableOrders_paginate"]/span/select')
                # Wait for the select element to become clickable
                wait = WebDriverWait(driver, 10)
                select_element = wait.until(EC.element_to_be_clickable(select_locator))
                # Wait for the options of the select element to load
                options_locator = (By.XPATH, '//*[@id="tableOrders_paginate"]/span/select/option')
                wait.until(EC.presence_of_all_elements_located(options_locator))

                # Proceed with interacting with the select element and its options
                select = Select(select_element)
                driver.execute_script("window.scrollTo(50, document.body.scrollHeight);")

                select.select_by_value(str(i))

                wait = WebDriverWait(driver, 100)
            wait.until(lambda driver: is_scrolled_to_top(driver))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Find the table you want to parse (adjust the selector as needed)
            table = soup.find("table")

            header_row = table.find("tr")
            header_cells = header_row.find_all("th")
            for cell in header_cells:
                headers.append(cell.text.strip())

            data_rows = table.find_all("tr")[1:]  # Skip the header row
            print(i)
            for row in data_rows:
                row_cells = row.find_all("td")

                # Check if a link exists in the status column
                status_cell = row_cells[7]  # Adjust the index for the status column
                status_link = status_cell.find("a")
                val=""
                if status_link:
                    status_link = status_link['href']
                    print(status_link)
                    driver.get('https://www.psacard.com/'+status_link)
                    wait = WebDriverWait(driver, 100)

                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bar-purple')))

                    element = driver.find_element(By.ID,'order-progress-bar')
                    e2=element.find_element(By.CLASS_NAME,'bar-purple')
                    val=e2.text
                    driver.back()
                row_data = [cell.text.strip() for cell in row_cells]
                if val!="":
                    row_data[7]=val
                rows.append(row_data)
    df=pd.DataFrame(rows)
    df=df.iloc[:,[2,7]]
    df.columns=['submission','status']
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT submission, status FROM orders"
    cursor.execute(query)
    db_data = cursor.fetchall()

    # Merge DataFrame and database data on 'submission'
    merged_data = pd.merge(df, pd.DataFrame(db_data, columns=['submission', 'status_db']), on='submission', how='outer')
    for index, row in merged_data.iterrows():
        submission = row['submission']
        status_df = row['status']
        status_db = row['status_db']

        if pd.notna(status_df) and pd.notna(status_db) and status_df != status_db:
            # Status has changed, update database
            update_query = f"UPDATE orders SET status = '{status_df}' WHERE submission = {submission}"
            cursor.execute(update_query)
            connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    driver.quit()

if __name__ == '__main__':
    main()
