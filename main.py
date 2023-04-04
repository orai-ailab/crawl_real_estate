from selenium import webdriver
import time
import undetected_chromedriver as uc
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
load_dotenv()
import logging

import pymongo
import certifi
logging.basicConfig(filename='current_url.log', level=logging.INFO,format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')

URL_MONGODB = os.environ.get("URL_MONGODB")
client = pymongo.MongoClient(URL_MONGODB,tlsCAFile=certifi.where())
database = client['facebook']
collection = database['id']

def create_browser(no_gui=False, proxy=None):
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        if no_gui:
            chrome_options.add_argument('--headless')
        if proxy:
            chrome_options.add_argument("--proxy-server={}".format(proxy))
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        browser_version = 'Failed to detect version'
        chromedriver_version = 'Failed to detect version'
        major_version_different = False

        if 'browserVersion' in browser.capabilities:
            browser_version = str(browser.capabilities['browserVersion'])

        if 'chrome' in browser.capabilities:
            if 'chromedriverVersion' in browser.capabilities['chrome']:
                chromedriver_version = str(browser.capabilities['chrome']['chromedriverVersion']).split(' ')[0]

        if browser_version.split('.')[0] != chromedriver_version.split('.')[0]:
            major_version_different = True
        print('_________________________________')
        print('Current web-browser version:\t{}'.format(browser_version))
        print('Current chrome-driver version:\t{}'.format(chromedriver_version))
        if major_version_different:
            print('warning: Version different')
            print(
                'Download correct version at "http://chromedriver.chromium.org/downloads" and place in "./chromedriver"')
        print('_________________________________')

        cookies = {'name': 'c_user', 'value': os.getenv('c_user'), 'domain': '.facebook.com', 'secure': True}
        cookies1 = {'name': 'xs', 'value': os.getenv('xs'), 'domain': '.facebook.com', 'secure': True}
        browser.get('https://www.facebook.com/')

        browser.add_cookie(cookies)
        browser.add_cookie(cookies1)
        browser.refresh()
        time.sleep(1)
        return browser

    # Thay thế "your_cookie_value_here" bằng giá trị cookie bạn đã sao chép
    


fileIds = 'post_ids.csv'
def readData(fileName):
    f = open(fileName, 'r', encoding='utf-8')
    data = []
    for i, line in enumerate(f):
        try:
            line = repr(line)
            line = line[1:len(line) - 3]
            data.append(line)
        except:
            print("err")
    return data

def writeFileTxt(fileName, content):
    with open(fileName, 'a') as f1:
        f1.write(content + os.linesep)

def getPostsGroup(driver, idGroup,current_url):
        if current_url == None:
            driver.get('https://mbasic.facebook.com/groups/' + str(idGroup))
        else:
            driver.get(current_url)
        time.sleep(2)
        file_exists = os.path.exists(fileIds)
        if (not file_exists):
            writeFileTxt(fileIds, '')

        sumLinks = readData(fileIds)
        while True:
            logging.info('Link current: '+driver.current_url)
            likeBtn = driver.find_elements(By.XPATH,'//*[contains(@id, "like_")]')
            if len(likeBtn):
                for id in likeBtn:
                    idPost = id.get_attribute('id').replace("like_", "")
                    if (idPost not in sumLinks):
                        sumLinks.append(idPost)
                        writeFileTxt(fileIds, idPost)
                        print(idPost)
            nextBtn = driver.find_elements(By.XPATH,'//a[contains(@href, "?bacr")]')
            if (len(nextBtn)):
                time.sleep(3)
                nextBtn[0].click()
                time.sleep(2)
            else:
                print('Next btn does not exist !')
                break



def clonePostContent(driver, postId = "1902017913316274"):
    try:
        driver.get("https://mbasic.facebook.com/" + str(postId))
        time.sleep(1)
        parrentImage = driver.find_elements(By.XPATH,"//div[@data-gt='{\"tn\":\"E\"}']")
        if (len(parrentImage) == 0):                
            parrentImage = driver.find_elements(By.XPATH,"//div[@data-ft='{\"tn\":\"E\"}']")

        contentElement = driver.find_elements(By.XPATH,"//div[@data-gt='{\"tn\":\"*s\"}']")
        if (len(contentElement) == 0):
            contentElement = driver.find_elements(By.XPATH,"//div[@data-ft='{\"tn\":\"*s\"}']")

        #get Content if Have
        if (len(contentElement)):
            content = contentElement[0].text

        #get Image if have
        linksArr = []
        if (len(parrentImage)):
            childsImage = parrentImage[0].find_elements(By.XPATH,".//*")
            for childLink in childsImage:
                linkImage = childLink.get_attribute('href')
                if (linkImage != None):
                    linksArr.append(linkImage.replace("m.facebook", "mbasic.facebook"))
        linkImgsArr = []
        if (len(linksArr)):
            linkImgsArr = []
            for link in linksArr:
                driver.get(link)
                linkImg = driver.find_elements(By.XPATH,'//*[@id="MPhotoContent"]/div[1]/div[2]/span/div/span/a[1]')
                linkImgsArr.append(linkImg[0].get_attribute('href'))

        postData = {"post_id": postId, "content" : "", "images": []}

        if (len(linkImgsArr)):
            postData["images"] = linkImgsArr
        if (len(contentElement)):
            postData["content"] = content
        print(postData)
        return postData
    except:
        return False




driver = create_browser()
getPostsGroup(driver, 'hanoihome', None)
#postIds = readData(fileIds)
#crawlPostData(driver, postIds, 'group')