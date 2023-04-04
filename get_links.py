import time, random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
import platform
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup

def init_browser():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    return browser

def get_links(link, max_page):
    browser = init_browser()
    w_file = open('links.txt', 'a', encoding='utf-8')
    for i in range(max_page):
        browser.get(link+'page/'+str(i+1))
        time.sleep(1)
        print('-----------------------Load page '+str(i+1)+' ----------------------')
        list = browser.find_elements(By.CLASS_NAME, 'mt-4')
        del list[0]
        for j in list:
            tag_a_href = j.find_element(By.TAG_NAME, 'a').get_attribute('href')
            w_file.write(tag_a_href+'\n')
        print('-----------------------Done page '+str(i+1)+' ----------------------')
            
    w_file.close()
    browser.close()


get_links('https://nhaphonet.vn/nha-dat/cho-thue-nha-ha-noi/', 70)