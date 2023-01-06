import time
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from datetime import datetime, timedelta
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from dependency.Pagesearch import find_domain, today_date
from typing import List, Dict, Any
from selenium.webdriver.chrome.options import Options
from tool.externalapi.bigquery_processor import bq_log_metrics
from webdriver_manager.chrome import ChromeDriverManager

base_url = "https://www.ettoday.net"
domain = find_domain(base_url)
today = today_date()


def start_scraper_ettoday_v3():
    year = today.year
    month = today.month
    day = today.day
    date_ranges = 1
    url = f"https://www.ettoday.net/news/news-list-{year}-{month}-{day}-0.htm"
    date_range_ago = (datetime.now() - timedelta(days=date_ranges))
    result_list: List[Dict[str, Any]] = list()
    options = Options()
    options.add_argument('headless')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Current session is {}".format(browser.session_id))
    try:
        browser.get(url)
    except exceptions.InvalidSessionIdException as g:
        print(g)
    time.sleep(2)
    print(f"{date_ranges}日前時間：", date_range_ago)
    try:
        last_height = browser.execute_script("return document.body.scrollHeight")
        go = True
        while go:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            html_source = browser.page_source
            soup = BeautifulSoup(html_source, "lxml")
            new_height = browser.execute_script("return document.body.scrollHeight")
            # 已經到頁面底部
            if new_height == last_height:
                print("已經到頁面最底部，程序停止")
                break
            last_height = new_height
            time.sleep(1)
            for f in soup.find(class_="part_list_2").find_all('h3'):
                if datetime.strptime(f.find(class_="date").text, '%Y/%m/%d %H:%M') < date_range_ago:
                    print(f"已經超出{date_range_ago}，程序停止")

                    go = False
                    break

                else:
                    print("目前畫面最下方文章的日期時間為：", f.find_all(class_="date")[-1].text)
        time.sleep(2)

        # 爬取已經拓展完的頁面

        user_agent = UserAgent().random

        headers = {
            "user-agent": user_agent

        }

        html_source = browser.page_source

        browser.close()

        print("Session {} closed".format(browser.session_id))
        soup = BeautifulSoup(html_source, "lxml")
        for d in soup.find(class_="part_list_2").find_all('h3'):
            if date_range_ago in d.select(".date"):
                pass
            else:
                print(d.find(class_="date").text, d.find_all('a')[-1].text)
                news = {"date": datetime.strptime(d.find(class_="date").text, "%Y/%m/%d %H:%M").isoformat(),
                        "title": d.find_all('a')[-1].text,
                        "link": base_url + d.find_all('a')[-1]["href"],
                        "category": d.find("em").text,
                        "log_datetime": datetime.now().isoformat()
                        }
                rep = requests.get(news['link'], headers=headers)
                sub_soup = BeautifulSoup(rep.text, 'lxml')
                content = [(i.get_text()).strip() for i in sub_soup.select("div.story > p ")]
                content = ''.join(content)
                news["content"] = content
                result_list.append(news)
                time.sleep(1)

    except Exception as e:
        print("Error", e)

    return result_list


if __name__ == '__main__':
    result_lists = start_scraper_ettoday_v3()
    print('saving to BQ')
    bq_log_metrics(today, domain, result_lists)
    print('accompleted job')