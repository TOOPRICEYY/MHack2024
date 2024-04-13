import time
# import pyautogui
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import zipfile
import os
import stat


def setup_browser():
    """Sets up the Selenium WebDriver by downloading ChromeDriver and setting it up."""
    chromedriver_url = "https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.122/mac-arm64/chromedriver-mac-arm64.zip"
    local_zip_path = "chromedriver.zip"
    
    # Download ChromeDriver
    response = requests.get(chromedriver_url)
    with open(local_zip_path, 'wb') as file:
        file.write(response.content)
    
    # Extract the ChromeDriver
    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver-mac-arm64/chromedriver")
    print(f"ChromeDriver path: {chromedriver_path}")  # Debugging: Print the path to verify
    
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver not found at path: {chromedriver_path}")
    
    os.chmod(chromedriver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment the following line to run Chrome in headless mode
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    
    os.remove(local_zip_path)
    
    return driver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_to_google_meet(driver, url, email, password):
    """Logs into Google Meet."""
    driver.get(url)
    
    # Wait for the email field to be present
    wait = WebDriverWait(driver, 80)  # Wait for up to 10 seconds
    email_field = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
    
    email_field.send_keys(email)
    email_field.send_keys(Keys.ENTER)
    
    # Wait for the password field to be present
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys(password)
    password_field.send_keys(Keys.ENTER)
    
    # Wait for some condition here that indicates the login process is complete

def capture_screen_with_selenium(driver, filename):
    driver.get_screenshot_as_file(filename)

def main():
    driver = setup_browser()
    try:
        login_to_google_meet(driver, "https://meet.google.com", "gcprice@umich.edu", "")
        time.sleep(5)  # Allow some time for the meeting page to load
        capture_screen_with_selenium(driver,"google_meet_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()