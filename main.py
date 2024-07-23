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
import urllib
import requests
from pathlib import Path
import re

def sanitize_folder_name(name):
    # Replace invalid characters with underscore
    sanitized_name = re.sub(r'[\/:*?"<>|]', '_', name)
    # Remove leading and trailing spaces or periods
    sanitized_name = sanitized_name.strip(' .')
    return sanitized_name

def rename_duplicates(videos):
    file_names, video_links = zip(*videos)
    name_count = {}
    renamed_list = []

    for name in file_names:
        if name in name_count:
            name_count[name] += 1
            renamed_list.append(f"{name}_{name_count[name]}")
            print(f"Duplicated file name, renaming {name} to {name}_{name_count[name]}")
        else:
            name_count[name] = 0
            renamed_list.append(name)

    renamed_videos = list(zip(renamed_list, video_links))
    return renamed_videos

def wait_for_loading(driver, target_type, target_name, patience=10, autoquit = True):
    try:
        # Wait for the specific element that indicates a successful redirection
        element_present = EC.presence_of_element_located((target_type, target_name))
        WebDriverWait(driver, patience).until(element_present)
        return
    except Exception as e:
        print(f"Waiting too long for {driver.current_url} ......\n{e}")
        if autoquit:
            driver.quit()
            sys.exit()

def get_video_links_by_type(driver, vtype):
    vtype_to_class_name = {
        'html': "activity.resource.modtype_resource",
        'mpeg': "activity.resource.modtype_resource",
        'evercam': "activity.evercam.modtype_evercam",
        'ewant': "activity.ewantvideo.modtype_ewantvideo"
    }
    file_names = []
    video_page_links = []
    video_links = []
    
    # obtain video page links
    page_elements = driver.find_elements(By.CLASS_NAME, vtype_to_class_name[vtype])
    for ele in page_elements:
        if vtype == 'html' or vtype == 'mpeg':
            icon = ele.find_element(By.TAG_NAME, "img").get_attribute("src")
            if vtype in icon:
                file_names.append(sanitize_folder_name(ele.find_element(By.CLASS_NAME, "instancename").text))
                video_page_links.append(ele.find_element(By.CLASS_NAME, "aalink").get_attribute("href"))
        else:
            file_names.append(sanitize_folder_name(ele.find_element(By.CLASS_NAME, "instancename").text))
            video_page_links.append(ele.find_element(By.CLASS_NAME, "aalink").get_attribute("href"))

    # Iterate over video pages and obtain mp4 links
    for idx, video_page_link in enumerate(video_page_links):
        driver.get(video_page_link)
        
        # Wait and get video link
        try:
            if vtype == 'mpeg' or vtype == 'ewant':
                wait_for_loading(driver, By.TAG_NAME, "video", autoquit = False)
                ele = driver.find_element(By.TAG_NAME, 'video')
                video_link = ele.find_element(By.TAG_NAME, 'source').get_attribute("src")
            elif vtype == 'html':
                wait_for_loading(driver, By.TAG_NAME, "iframe", autoquit = False)
                video_link = driver.find_element(By.TAG_NAME, 'iframe').get_attribute("src")
                video_link = video_link.replace("index.html?embed=1", "media.mp4")
            elif vtype == 'evercam':
                wait_for_loading(driver, By.TAG_NAME, "iframe", autoquit = False)
                
                # Switch to iframe
                iframe = driver.find_element(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(iframe)
                
                # Locate video wrapup by searching video tag
                video_link = driver.find_element(By.TAG_NAME, "video").get_attribute("src")

                # Leave the iframe
                driver.switch_to.default_content()
            
            video_links.append(video_link)
        
        except Exception as e:
            # Delete corresponding file_name
            skipped = file_names.pop(idx - len(video_page_links))
            print(f"Skipping {skipped}: Unable to locate video tag\n{e}")
        
        # Back to course page
        driver.back()
        wait_for_loading(driver, By.TAG_NAME, "footer")

    results = list(zip(file_names, video_links))
    print(f'Found {len(results)} videos of type {vtype}')
    return results

# Obtain username and password
username = input("Enter username (Student ID):")
password = input("Enter password:")

# Set up Chrome driver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment if you want to run headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Log in the NYCU portal
driver.get("https://portal.nycu.edu.tw/#/login")
wait_for_loading(driver, By.CSS_SELECTOR, "input[type='submit']")
username_field = driver.find_element(By.ID, "account")
password_field = driver.find_element(By.ID, "password")
username_field.send_keys(username)
password_field.send_keys(password)
login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
login_button.click()
wait_for_loading(driver, By.XPATH, "//span[@class='no-redirect' and contains(text(), '首頁 Home')]")

# Open the new E3 course history
driver.get("https://portal.nycu.edu.tw/#/redirect/newe3")
wait_for_loading(driver, By.ID, "user-action-menu")
driver.get("https://e3.nycu.edu.tw/local/courseextension/course_history.php")
wait_for_loading(driver, By.ID, "page-footer")

# Loop over courses and download videos
try:
    # Create a base directory for the videos
    base_dir = Path("./videos")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all course links within course history
    course_links = driver.find_elements(By.CLASS_NAME, "course-link")
    course_counts = len(course_links)

    # Loop over all the course links, excluding "[學生]1112.醫五核心實習訓練與課程相關"
    for cnt in range(course_counts - 1):
        # Redefine link elements to prevent stale element exception
        link = driver.find_elements(By.CLASS_NAME, "course-link")[cnt]
        course_name = link.text
        sanitized_course_name = sanitize_folder_name(course_name)
        course_folder = base_dir / sanitized_course_name
        course_folder.mkdir(parents=True, exist_ok=True)
        
        # Head to specific course
        link.click()
        wait_for_loading(driver, By.TAG_NAME, "footer")
        print(sanitized_course_name)
        videos = []
        
        # Obatin video names and links of different types
        videos += get_video_links_by_type(driver, "html")
        videos += get_video_links_by_type(driver, "mpeg")
        videos += get_video_links_by_type(driver, "evercam")
        videos += get_video_links_by_type(driver, "ewant")

        # Check and rename duplicated filenames
        if videos:
            videos = rename_duplicates(videos)
        
        # Download video with urllib
        for video in videos:
            video_file_path = course_folder / f"{video[0]}.mp4"
            if video_file_path.exists():
                print(f"Skipping {video_file_path}: Video already exists")
            else:
                # set requests' cookies
                cookies = driver.get_cookies()
                s = requests.Session()
                for cookie in cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
                
                # download by read/write
                response = s.get(video[1], stream=True)
                print(f"Status code = {response.status_code}, Downloading: {video[1]}")
                with open(video_file_path, 'wb') as f:
                    f.write(response.content)
                            
        # Back to course history
        driver.back()
        wait_for_loading(driver, By.ID, "page-footer")

except Exception as e:
    print("An error occurred:", e)

# Close the browser
driver.quit()
