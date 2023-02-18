import json
import random
import time
import traceback
import requests

from datetime import datetime
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
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
    num = 0
    try:
        last_div = None
        like_count = None
        go = True
        last_height = browser.execute_script("return document.body.scrollHeight")
        while go:
            html_source = browser.page_source
            soup = BeautifulSoup(html_source, "lxml")

            user_agent = UserAgent().random

            headers = {
                "user-agent": user_agent

            }

            divs = soup.find('div', class_='e7-container mb-5').find_all('div', class_='e7-container')
            last_title = soup.find_all('span', 'e7-show-if-device-is-not-xs')[-1].text

            print('last title: ', last_title)
            last_pos = browser.find_elements(By.CLASS_NAME, 'e7-container')[-1]
            try:
                divs = divs[divs.index(last_div):]

            except:
                pass
            try:
                for d in divs:
                    try:
                        like_count = d.find('div', class_='e7-recommendScore text-no-wrap f11').text
                        print('like count color: RED')
                    except:
                        try:
                            like_count = d.find('div', class_='e7-recommendScore text-no-wrap e7-grey-text').text
                            print('like count color: GREY')
                        except:
                            try:
                                like_count = d.find('div', class_='e7-recommendScore text-no-wrap f13').text
                                print('like count color: YELLOW')
                            except:
                                try:
                                    like_count = d.find('div', class_='e7-recommendScore text-no-wrap f12').text
                                    print('like count color: GREEN')
                                except:
                                    print('by pass this row data')
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
                    print(ptt_dict["title"], ptt_dict["link"])
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
                    last_div = divs[-1]

                    time.sleep(random.uniform(2, 5))
            except:
                pass

            browser.execute_script("arguments[0].scrollIntoView();", last_pos)
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("already scroll to bottom!")
                break
            last_height = new_height
            time.sleep(random.uniform(2, 5))

            num += 1
            print('expand page count: ', num)
        browser.close()
        print("Session {} closed".format(browser.session_id))

    except Exception:
        print(traceback.format_exc())

    return result_list


if __name__ == '__main__':
    result_lists = ptt_crawl()
    print('total count: ', len(result_lists))
    bq_ptt_metrics(today, domain, result_lists)
