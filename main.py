from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment if you want to run headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the NYCU login page
driver.get("https://portal.nycu.edu.tw/#/login")

# Allow the page to load
time.sleep(3)  # Wait for the page to load, adjust this if necessary

# Find the username and password fields
username_field = driver.find_element(By.ID, "account")
password_field = driver.find_element(By.ID, "password")

# Enter the username and password
username_field.send_keys("10701129")
password_field.send_keys("fa1688MI7215ly")

# Find and click the login button
login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
login_button.click()

# Allow some time for the login to process
time.sleep(5)

# Verify successful login
try:
    # Wait for the specific element that indicates a successful login
    element_present = EC.presence_of_element_located((By.XPATH, "//span[@class='no-redirect' and contains(text(), '首頁 Home')]"))
    WebDriverWait(driver, 10).until(element_present)
    print("Login successful!")
except:
    print("Login failed!")

# Open the new E3 course history
driver.get("https://portal.nycu.edu.tw/#/redirect/newe3")
time.sleep(5)
driver.get("https://e3.nycu.edu.tw/local/courseextension/course_history.php")
time.sleep(5)

# Verify redirection
try:
    # Wait for the specific element that indicates successful redirection
    element_present = EC.presence_of_element_located((By.XPATH, "//div[@class='layer2_left_caption' and contains(text(), '歷年課程')]"))
    WebDriverWait(driver, 20).until(element_present)
    print("Redirection successful!")
except:
    print("Redirection failed!")

# Close the browser
driver.quit()
