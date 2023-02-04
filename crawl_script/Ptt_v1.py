import random
import time
import traceback
import requests

from datetime import datetime
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from dependency.Pagesearch import today_date
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_ptt_metrics

base_url = 'https://www.pttweb.cc'
today = today_date()
domain = DomainName.PTT.value


def ptt_crawl():
    url = 'https://www.pttweb.cc/hot/all/today'
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
        print('session error: ', g)
    time.sleep(2)
    try:
        last_height = browser.execute_script("return document.body.scrollHeight")
        go = 0
        while go <= 5:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            html_source = browser.page_source
            soup = BeautifulSoup(html_source, "lxml")
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("已經到頁面最底部，程序停止")
                break
            last_height = new_height
            time.sleep(2)
            print("目前畫面最下方文章為：", soup.find_all(class_="e7-show-if-device-is-not-xs")[-1].text)
            go += 1
        time.sleep(2)

        user_agent = UserAgent().random

        headers = {
            "user-agent": user_agent

        }

        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "lxml")

        divs = soup.find('div', class_='e7-container mb-5').find_all('div', class_='e7-container')
        for d in divs:
            like_count = None
            try:
                like_count = d.find('div', class_='e7-recommendScore text-no-wrap f11').text
            except:
                try:
                    like_count = d.find('div', class_='e7-recommendScore text-no-wrap e7-grey-text').text
                except:
                    try:
                        like_count = d.find('div', class_='e7-recommendScore text-no-wrap f13').text
                    except:
                        try:
                            like_count = d.find('div', class_='e7-recommendScore text-no-wrap f12').text
                        except:
                            continue

            ptt_dict = {
                "date": None,
                "title": d.find('span', 'e7-show-if-device-is-not-xs').text,
                "link": base_url + d.find('a', class_="e7-article-default")["href"],
                "content": None,
                "category": d.find('a', class_='e7-boardName').find('span', class_='e7-link-to-article').text,
                "like_count": like_count,
                "comment_count": d.find('div', class_='e7-recommendCount text-no-wrap e7-grey-text').text,
                "log_datetime": datetime.now().isoformat()

            }

            rep = requests.get(ptt_dict['link'], headers=headers)
            sub_soup = BeautifulSoup(rep.text, 'lxml')
            date = sub_soup.find('time').text
            date = datetime.strptime(date, "%Y/%m/%d %H:%M").isoformat()
            ptt_dict["date"] = date
            content = [(i.get_text()).strip() for i in sub_soup.select("div.e7-main-content > span ")]
            content = ''.join(content).split("--")[:-1]
            content = "--".join(content)
            ptt_dict["content"] = content
            result_list.append(ptt_dict)
            time.sleep(random.uniform(5, 10))
        browser.close()
        print("Session {} closed".format(browser.session_id))

    except Exception:
        print(traceback.format_exc())

    return result_list


#
if __name__ == '__main__':
    result_lists = ptt_crawl()
    bq_ptt_metrics(today, domain, result_lists)
