from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import schedule
import time
import pandas as pd
from email_utils import send_email
from config import *
from datetime import datetime

def check_local_inventory(product_name):
    try:
        inventory = pd.read_csv("inventory.csv")
        item = inventory[inventory["product"] == product_name]
        if not item.empty:
            return int(item["quantity"].values[0])
        else:
            return None
    except Exception as e:
        print(f"Error reading inventory.csv: {e}")
        return None

def update_local_inventory(product_name, new_quantity):
    try:
        inventory = pd.read_csv("inventory.csv")
        if product_name in inventory['product'].values:
            inventory.loc[inventory['product'] == product_name, 'quantity'] = new_quantity
            inventory.to_csv("inventory.csv", index=False)
            print(f"Local inventory updated: {product_name} = {new_quantity}")
        else:
            print(f"Product {product_name} not found in inventory to update.")
    except Exception as e:
        print(f"Error updating inventory.csv: {e}")

def deduct_inventory(product_name, quantity_to_deduct):
    current_quantity = check_local_inventory(product_name)
    if current_quantity is not None:
        new_quantity = max(current_quantity - quantity_to_deduct, 0)
        update_local_inventory(product_name, new_quantity)
    else:
        print(f"Cannot deduct inventory; product {product_name} not found.")

def check_stock():
    print(f"[{datetime.now()}] Starting stock check...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
        driver.get(AMAZON_URL)

        inventory = pd.read_csv("inventory.csv")
        
        for index, row in inventory.iterrows():
            product_name = row["product"]
            product_id = product_name.replace(' ', '')  # remove spaces for ID construction
            print(f"Checking stock for product: {product_name}")

            stock_element_id = f"stock-id-{product_id}"

            try:
                stock_text = driver.find_element(By.ID, stock_element_id).text.strip()
                stock = int(stock_text)
                print(f"Current Amazon stock for {product_name}: {stock}")

                if stock < 5:
                    send_email("Stock Low", f"Amazon stock for {product_name} is {stock}. Checking local inventory...")
                    local_stock = check_local_inventory(product_name)

                    if local_stock is None:
                        send_email("Inventory Error", f"{product_name} not found in local inventory.")
                        print(f"{product_name} not found in inventory.")
                    elif local_stock > 0 and stock <= 2:
                        # Update stock on Amazon UI
                        stock_input_id = f"stock-input-{product_id}"
                        update_button_id = f"update-button-{product_id}"

                        driver.find_element(By.ID, stock_input_id).clear()
                        driver.find_element(By.ID, stock_input_id).send_keys("10")
                        driver.find_element(By.ID, update_button_id).click()
                        
                        # Deduct local inventory by the amount replenished (10 - current stock)
                        deduct_inventory(product_name, 10 - stock)

                        send_email("Stock Updated", f"Amazon stock for {product_name} was low ({stock}). Updated to 10. Local inventory updated.")
                        print(f"Stock updated on Amazon and inventory deducted for {product_name}.")
                    else:
                        send_email("Inventory Empty", f"{product_name} has no local stock.")
                        print(f"Local inventory empty for {product_name}.")
                else:
                    print(f"Amazon stock sufficient for {product_name}.")

            except Exception as e:
                print(f"Could not get stock info for {product_name}: {e}")
                send_email("Stock Info Error", f"Could not get stock info for {product_name}: {e}")

    except Exception as e:
        send_email("Error", str(e))
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()
        print("Stock check completed.\n")

print(f"Monitoring Amazon URL: {AMAZON_URL}")
print(f"Check interval set to every {CHECK_INTERVAL_MINUTES} minutes.")
print("Automation script started.\n")

schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_stock)

while True:
    schedule.run_pending()
    time.sleep(1)
