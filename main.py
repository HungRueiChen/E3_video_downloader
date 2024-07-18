import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib
from pathlib import Path
import re

def sanitize_folder_name(name):
    # Replace invalid characters with underscore
    sanitized_name = re.sub(r'[\/:*?"<>|]', '_', name)
    # Remove leading and trailing spaces or periods
    sanitized_name = sanitized_name.strip(' .')
    return sanitized_name

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
time.sleep(3)

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
time.sleep(3)
driver.get("https://e3.nycu.edu.tw/local/courseextension/course_history.php")
time.sleep(3)

# Verify redirection
try:
    # Wait for the specific element that indicates successful redirection
    element_present = EC.presence_of_element_located((By.XPATH, "//div[@class='layer2_left_caption' and contains(text(), '歷年課程')]"))
    WebDriverWait(driver, 20).until(element_present)
    print("Redirection successful!")
except:
    print("Redirection failed!")

# Loop over courses and download videos
try:
    # Find the parent element that contains the course links
    parent_element = driver.find_element(By.CLASS_NAME, "layer2_left_caption")
    
    # Find all course links within the parent element
    course_links = parent_element.find_elements(By.CLASS_NAME, "course-link")

    # Create a base directory for the videos
    base_dir = Path("./videos")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Loop over all the course links and print their text
    for link in course_links[10:15]:
        course_name = link.text
        sanitized_course_name = sanitize_folder_name(course_name)
        course_folder = base_dir / sanitized_course_name
        course_folder.mkdir(parents=True, exist_ok=True)
        
        link.click()
        time.sleep(3)  # Adjust this if necessary
        
        # Find RESOURCES and EVERCAM
        resources_elements = driver.find_elements(By.CLASS_NAME, "activity.resource.modtype_resource")
        evercam_elements = driver.find_elements(By.CLASS_NAME, "activity.evercam.modtype_evercam")
        iframe_elements = resources_elements + evercam_elements
        print(f'{course_name}: found {len(iframe_elements)} videos of types RESOURCES or EVERCAM')
        
        for element in iframe_elements[:2]:
            video_page_link = element.find_element(By.CLASS_NAME, "aalink").get_attribute("href")
            driver.get(video_page_link)
            file_name = driver.find_element(By.TAG_NAME, "h2").text
            
            # Switch to iframe
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(iframes[0])
            
            # Locate video wrapup by searching video tag
            video_link = driver.find_element(By.TAG_NAME, "video").get_attribute("src")
            
            # Download video with urllib
            video_file_path = course_folder / f"{sanitize_folder_name(file_name)}.mp4"
            urllib.request.urlretrieve(video_link, video_file_path)
            print(f"Downloaded: {video_file_path}")
            
            # Leave the iframe
            driver.switch_to.default_content()

            driver.back()
            time.sleep(3)  # Adjust this if necessary
            
        driver.back()
        time.sleep(3)  # Adjust this if necessary

        # Find OTHER DATATYPES

except Exception as e:
    print("An error occurred:", e)

# Close the browser
driver.quit()
