from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import concurrent.futures
import itertools
import time
import csv
import os

# ----------------------------------------------------------------------------------------
# ◾️◾️◾️◾️編集するパラメーター◾️◾️◾️◾️
# ----------------------------------------------------------------------------------------

# 検索回数
SEARCH_NUM = 100

# csvのpathと名前指定
CSV_PATH = "google_search_result.csv"

# 並列処理する時に使用するCPUの数。
# プログラムを走らせた際、処理が重ければ、「2」など値を直指定してチューニングする
# 例： 
# CPU_NUM=2
CPU_NUM=os.cpu_count()

# PCのユーザーエージェントを設定
# Key: CSVに出力される名称
# Value: chromeに設定されるユーザーエージェント
# 以下のようなサイトで検索してくる
# URL:https://qiita.com/kapiecii/items/093ffd6f0b09ad775250
PC_USER_AGENTS = {
    "mac_chrome": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3864.0 Safari/537.36",
    "mac_firefox": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0",
}

# スマホのユーザーエージェントを設定
# PC画面とスマホ画面で取得する方法が異なるため、PCとスマホで分けている
SP_USER_AGENTS = {
    "iphonex_safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1"
}

# Key: CSVに出力される地域名
# Value: chromeに設定される地域（latitude, longitudeを編集する）
# googlemapで検索できる(場所を指定して、右クリックすると緯度経度が表示される)
# latitude：緯度
# longitude：経度
# accuracy：精密さ
locations = {
    "北海道": {
        "latitude": 43.80194143971396,
        "longitude": 142.48668592916096,
        "accuracy": 100,
    },
    "大阪": {
        "latitude": 34.69788906157618,
        "longitude": 135.4905187212909,
        "accuracy": 100,
    },
    "東京": {
        "latitude": 35.68378001134092,
        "longitude": 139.79304370713152,
        "accuracy": 100,
    }
}

# 検索するキーワード
keywords = [
    "営業代行",
    "MEO",
    "RPA"
]


# 以上、編集するパラメーター
# ----------------------------------------------------------------------------------------













# ----------------------------------------------------------------------------------------
# 以下は編集不要
# ----------------------------------------------------------------------------------------

CHROMEDRIVER = "./chromedriver"

def get_driver(user_agent, location_dic):
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": False
    })
    options.add_argument('user-agent={0}'.format(user_agent))
    options.add_argument('--headless')
    options.add_argument('--disable-gpu') 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": "https://www.google.co.jp/",
            "permissions": ["geolocation"]
        },
    )

    # 緯度、経度、緯度・経度の誤差(単位：m)を設定する
    driver.execute_cdp_cmd(
        "Emulation.setGeolocationOverride",
        location_dic,
    )

    driver.execute_cdp_cmd(
        "Emulation.setLocaleOverride",
        location_dic,
    )
    driver.delete_all_cookies()

    driver.set_window_size('1200', '1000')
    return driver


def scraping_sp(scraping_results, keyword, user_agent_key, user_agent_value, location_key, location_value, index):
    driver = get_driver(user_agent_value, location_value)
    driver.get("https://www.google.co.jp/")

    search = driver.find_element_by_name('q')
    search.send_keys(keyword)
    search.submit()


    elements = driver.find_elements_by_xpath("//div[@data-text-ad='1']")
    print(len(elements))
    for element in elements:
        subject = element.find_element_by_css_selector(".V7Sr0.p5AXld.PpBGzd.YcUVQe.tgGIB").text
        url = element.find_element_by_css_selector(".C8nzq.d5oMvf.BmP5tf").get_attribute("href")
        text = ""
        try:
            text = BeautifulSoup(element.find_element_by_css_selector(".MUxGbd.yDYNvb.lEBKkf").get_attribute("textContent"), 'lxml').get_text()
        except:
            text = BeautifulSoup(element.find_element_by_css_selector(".MUxGbd.yDYNvb.aLF0Z").get_attribute("textContent"), 'lxml').get_text()

        scraping_results.append([
            keyword,
            location_key,
            user_agent_key,
            subject,
            url,
            text,
            index + 1
        ])

    driver.close()
    
    return scraping_results

def scraping_pc(scraping_results, keyword, user_agent_key, user_agent_value, location_key, location_value, index):
    driver = get_driver(user_agent_value, location_value)

    driver.get("https://www.google.co.jp/")
    search = driver.find_element_by_name('q')
    search.send_keys(keyword)
    search.submit()


    elements = driver.find_elements_by_xpath("//div[@data-text-ad='1']")
    print(len(elements))
    for element in elements:
        subject = element.find_element_by_css_selector(".cfxYMc.JfZTW.c4Djg.MUxGbd.v0nnCb").text
        url = element.find_element_by_css_selector(".Krnil").get_attribute("href")
        text = BeautifulSoup(element.find_element_by_css_selector(".MUxGbd.yDYNvb.lyLwlc").get_attribute("textContent"), 'lxml').get_text()

        scraping_results.append([
            keyword,
            location_key,
            user_agent_key,
            subject,
            url,
            text,
            index + 1
        ])

    driver.close()

    return scraping_results

if __name__ == "__main__":
    start = time.time()
    f = open(CSV_PATH, "w")
    writer = csv.writer(f)

    writer.writerow([
        "ID",
        "キーワード",
        "エリア",
        "デバイス",
        "広告タイトル",
        "URL",
        "文章",
        "検索回数"
    ])
    f.close()

      

    scraping_results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=CPU_NUM)
    for keyword in keywords:
        for location_key, location_value in locations.items():
            for user_agent_key, user_agent_value in SP_USER_AGENTS.items():
                for index in range(SEARCH_NUM):
                    executor.submit(scraping_sp, scraping_results, keyword, user_agent_key, user_agent_value, location_key, location_value, index)
            for user_agent_key, user_agent_value in PC_USER_AGENTS.items():
                for index in range(SEARCH_NUM):
                    executor.submit(scraping_pc, scraping_results, keyword, user_agent_key, user_agent_value, location_key, location_value, index)
    executor.shutdown()
    with open(CSV_PATH, "a") as f:
        writer = csv.writer(f)
        for index, scraping_result in enumerate(scraping_results):
            scraping_result.insert(0, index)
            writer.writerow(scraping_result)
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")