# Hướng dẫn lấy cookie Facebook bằng Chrome và auto login Selenium bằng cookie đó

Lưu ý trước khi thực hiện: việc lấy cookie Facebook của người dùng mà không được sự cho phép của họ có thể vi phạm chính sách quyền riêng tư của Facebook và có thể dẫn đến việc bị khóa tài khoản. Do đó, hãy sử dụng phương pháp này với mục đích hợp lệ và hợp pháp.

* Bước 1: Đăng nhập vào tài khoản Facebook của bạn bằng trình duyệt Chrome.

* Bước 2: Sau khi đăng nhập thành công, nhấn phím F12 để mở cửa sổ Developer Tools. Chọn tab "Application" và sau đó chọn "Cookies" ở cột bên trái.

* Bước 3: Tiếp theo, bạn cần tìm tên domain của Facebook trong danh sách Cookies. Chọn domain đó và bạn sẽ thấy danh sách các cookie hiện tại của bạn. Tìm kiếm cookie `c_user` và `xs` và sao chép giá trị của chúng.

* Bước 4: Tạo một script Python bằng thư viện Selenium để đăng nhập tự động bằng Cookie này.

```python
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--start-maximized")

# Thay thế "your_cookie_value_here" bằng giá trị cookie bạn đã sao chép
cookies = {'name': 'c_user', 'value': 'your_cookie_value_here', 'domain': '.facebook.com', 'secure': True}
cookies1 = {'name': 'xs', 'value': 'your_cookie_value_here', 'domain': '.facebook.com', 'secure': True}

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('https://www.facebook.com/')

driver.add_cookie(cookies)
driver.add_cookie(cookies1)

driver.refresh()
```


## Giới thiệu
Đây là mã nguồn Python để crawl danh sách post từ group facebook và lấy nội dung của từng post.

## Yêu cầu hệ thống
- Cài đặt Python 3.5 trở lên
- Sử dụng các thư viện: selenium, undetected_chromedriver, pymongo, os, logging, ... 

## Cài đặt
1. Chạy lệnh sau để cài đặt các thư viện cần thiết:

```
pip install selenium undetected-chromedriver pymongo python-dotenv webdriver-manager
```

2. Cần cung cấp đường dẫn đến MongoDB cho việc lưu trữ danh sách các post đã crawl. Điều này có thể được đặt thông qua biến môi trường `URL_MONGODB`.


## Sử dụng

**1. Khởi tạo và cấu hình selenium driver**

```python
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
            print('Warning: Version different')
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
```

**2. Lấy danh sách các post từ group facebook**

```python
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

```

**3. Lấy tham số và nội dung của các post**

```python
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
```

**4. Thực thi chương trình**

```python
driver = create_browser()
getPostsGroup(driver, 'hanoihome', None)
#postIds = readData(fileIds)
#crawlPostData(driver, postIds, 'group')
```
Chạy chương trình trên sẽ ứng dụng các hàm trên để crawl các post của group facebook "hanoihome" và lấy các thông tin của từng post.
