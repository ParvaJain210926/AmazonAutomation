from selenium import webdriver
from selenium.webdriver.common.by import By
import schedule
import time
import pandas as pd
from email_utils import send_email
from config import *

def check_stock():
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)  # or use Edge
    driver.get(AMAZON_URL)

    try:
        stock_text = driver.find_element(By.ID, "stock-id").text  # Replace with correct ID
        stock = int(stock_text.strip())

        if stock < 5:
            send_email("Stock Low", f"Current stock is {stock}. Checking local inventory...")

            inventory = pd.read_csv("inventory.csv")  # or use sqlite3
            item = inventory[inventory["product"] == "YourProduct"]
            local_stock = int(item["quantity"].values[0])

            if local_stock > 0:
                if stock <= 2:
                    # Update stock (depends on seller central login and UI)
                    driver.find_element(By.ID, "stock-input").clear()
                    driver.find_element(By.ID, "stock-input").send_keys("10")
                    driver.find_element(By.ID, "update-button").click()
                    
                    send_email("Stock Updated", "Stock was low. Automatically updated to 10.")
            else:
                send_email("Inventory Empty", "Stock low and local inventory is empty. Manual action needed.")

    except Exception as e:
        send_email("Error", str(e))
    finally:
        driver.quit()

# Scheduler
schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_stock)

while True:
    schedule.run_pending()
    time.sleep(1)