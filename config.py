from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# Other constants (keep these)
AMAZON_URL = "https://sellercentral.amazon.in/path-to-your-product"
CHROME_DRIVER_PATH = "chromedriver.exe"
EDGE_DRIVER_PATH = "msedgedriver.exe"
CHECK_INTERVAL_MINUTES = 2
