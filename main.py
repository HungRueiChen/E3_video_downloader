import os
import sys
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

def wait_for_loading(driver, target_type, target_name, patience=10):
    try:
        # Wait for the specific element that indicates a successful redirection
        element_present = EC.presence_of_element_located((target_type, target_name))
        WebDriverWait(driver, patience).until(element_present)
        return
    except Exception as e:
        print("Waiting too long for {driver.current_url} ......\n{e}")
        driver.quit()
        sys.exit()


def get_video_links_by_type(driver, vtype):
    vtype_to_class_name = {
        'resource': "activity.resource.modtype_resource",
        'evercam': "activity.evercam.modtype_evercam",
        'ewant': "activity ewantvideo modtype_ewantvideo"
    }
    results = []
    # obtain video page links
    page_elements = driver.find_elements(By.CLASS_NAME, vtype_to_class_name[vtype])
    if vtype == 'resource':
        video_page_links = []
        for ele in page_elements:
            icon = ele.find_elements(By.TAG_NAME, "img").get_attribute("src")
            if 'pdf' not in icon:
                video_page_links.append(ele.find_element(By.CLASS_NAME, "aalink").get_attribute("href"))
    else:
        video_page_links = [x.find_element(By.CLASS_NAME, "aalink").get_attribute("href") for x in page_elements]
    print(f'Found {len(video_page_links)} videos of type {vtype}')
    
    # iterate over video pages and obtain mp4 links
    for video_page_link in video_page_links:
        driver.get(video_page_link)
        


# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment if you want to run headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the NYCU login page
driver.get("https://portal.nycu.edu.tw/#/login")
wait_for_loading(driver, By.CSS_SELECTOR, "input[type='submit']")

# Find the username and password fields
username_field = driver.find_element(By.ID, "account")
password_field = driver.find_element(By.ID, "password")

# Enter the username and password
username_field.send_keys("10701129")
password_field.send_keys("fa1688MI7215ly")

# Find and click the login button
login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
login_button.click()
wait_for_loading(driver, By.XPATH, "//span[@class='no-redirect' and contains(text(), '首頁 Home')]")


# Open the new E3 course history
driver.get("https://portal.nycu.edu.tw/#/redirect/newe3")
wait_for_loading(driver, By.ID, "user-action-menu")
driver.get("https://e3.nycu.edu.tw/local/courseextension/course_history.php")
wait_for_loading(driver, By.XPATH, "//div[@class='layer2_left_caption' and contains(text(), '歷年課程')]")


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
    for link in course_links[12:13]:
        course_name = link.text
        sanitized_course_name = sanitize_folder_name(course_name)
        course_folder = base_dir / sanitized_course_name
        course_folder.mkdir(parents=True, exist_ok=True)
        
        link.click()
        time.sleep(3)  # Adjust this if necessary
        print(sanitized_course_name)
        
        # Find RESOURCES and EVERCAM
        resources_elements = driver.find_elements(By.CLASS_NAME, "activity.resource.modtype_resource")
        evercam_elements = driver.find_elements(By.CLASS_NAME, "activity.evercam.modtype_evercam")
        iframe_elements = resources_elements + evercam_elements
        video_page_links = [x.find_element(By.CLASS_NAME, "aalink").get_attribute("href") for x in iframe_elements]
        print(f'{course_name}: found {len(video_page_links)} videos of types RESOURCES or EVERCAM')
        
        for video_page_link in video_page_links:
            driver.get(video_page_link)
            time.sleep(3)
            
            try:
                file_name = driver.find_element(By.TAG_NAME, "h2").text
                
                # Switch to iframe
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(iframes[0])
                
                # Locate video wrapup by searching video tag
                video_link = driver.find_element(By.TAG_NAME, "video").get_attribute("src")
                
                # Download video with urllib
                video_file_path = course_folder / f"{sanitize_folder_name(file_name)}.mp4"
                if not video_file_path.exists():
                    urllib.request.urlretrieve(video_link, video_file_path)
                    print(f"Downloaded: {video_file_path}")
                else:
                    print(f"Skipping {video_file_path}: Video already exists")
                
                # Leave the iframe
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"Skipping {video_page_link}: {e}")
            
            driver.back()
            time.sleep(3)  # Adjust this if necessary
            
        driver.back()
        time.sleep(3)  # Adjust this if necessary

        # Find EWANTVIDEO
        # Find OTHER DATATYPES

except Exception as e:
    print("An error occurred:", e)

# Close the browser
driver.quit()
