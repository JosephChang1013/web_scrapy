import time
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from datetime import datetime, timedelta
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from dependency.Pagesearch import today_date
from typing import List, Dict, Any
from selenium.webdriver.chrome.options import Options

from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_log_metrics
from webdriver_manager.chrome import ChromeDriverManager

base_url = "https://news.tvbs.com.tw"
domain = DomainName.TVBSNEWS.value
today = today_date()


def start_scraper_tvbs_v1():
    url = "https://news.tvbs.com.tw/realtime"
    date_ranges = 1
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
            for f in soup.find(class_="news_list").find(class_="list").find_all('li'):
                if f:
                    try:
                        print("目前畫面最下方文章的日期時間為：", f.find('div', class_='time').text)
                    except:
                        pass
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
        for d in soup.find(class_="news_list").find(class_="list").find_all('li'):
            if d:
                try:
                    if date_range_ago in d.find('div', class_='time'):
                        pass
                    else:
                        print(d.find('div', class_='time').text, d.find_all('a')[0].text)
                        news = {"date": datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").isoformat(),
                                "title": d.find('h2', class_='txt').text,
                                "link": base_url + d.find('a')['href'],
                                "category": d.find(class_="type").text,
                                "log_datetime": datetime.now().isoformat(),
                                }
                        rep = requests.get(news['link'], headers=headers)
                        sub_soup = BeautifulSoup(rep.text, 'lxml')
                        content = [(i.get_text()).strip() for i in sub_soup.select("div.article_content > p ")]
                        content = ''.join(content)
                        news["content"] = content
                        result_list.append(news)
                        time.sleep(1)
                except:
                    pass
    except Exception as e:
        print("Error", e)

    return result_list


if __name__ == '__main__':
    result_lists = start_scraper_tvbs_v1()
    print('saving to BQ', result_lists[0])
    bq_log_metrics(today, domain, result_lists)
    print('accompleted job')
