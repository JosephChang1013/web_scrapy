import json
import time

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
from tool.externalapi.bigquery_processor import bq_dcard_metrics
from datetime import datetime, timedelta, date

today = today_date()
domain = DomainName.DCARD.value


def Dcard_crawl():
    # set variables for data retrieval
    three_date_ago = (date.today() - timedelta(days=3))

    # set the limit of posts to retrieve
    limit = '200'

    url = f'https://pttbrain-api.herokuapp.com/api/dcard/metric/hot-posts?since={three_date_ago}&limit={limit}&offset=0'
    result_list: List[Dict[str, Any]] = list()
    user_agent = UserAgent().random
    options = Options()  # set options for the browser
    options.add_argument('headless')  # run browser in headless mode
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--user-agent=%s' % user_agent)   # set the user agent for the browser
    options.add_argument('--remote-debugging-port=9222')

    # create a Chrome browser instance
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Current session is {}".format(browser.session_id))

    try:
        browser.get(url)  # navigate to the url
    except exceptions.InvalidSessionIdException as g:
        print(g)
    time.sleep(2)
    html_source = browser.page_source  # retrieve the page source
    soup = BeautifulSoup(html_source, "lxml")
    r = soup.find('pre').text
    chapters = json.loads(r)

    for index, chapter in enumerate(chapters['data']):
        print('No:', index + 1)
        print('title:', chapter['title'])
        print('date', chapter['created_at'])
        print('content:', chapter['content'])
        print('like:', chapter['num_reactions'])
        id_ = chapter['id']

        # store the post title, date, content, link ... in dcard_dict
        dcard_dict = {
            "title": chapter['title'],
            "date": datetime.strptime(chapter['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None).isoformat()[
                    :-7],
            "content": chapter['content'],
            "link": f"https://www.dcard.tw/f/talk/p/{id_}",
            "category": chapter['forum']['name'],
            "like_count": chapter['num_reactions'],
            "log_datetime": datetime.now().isoformat()
        }
        result_list.append(dcard_dict)

        # ------ 以下抓取留言 但 BRAIN PTT 無留言可抓 ------
        # id_ = chapter['id']

        # if chapter['commentCount'] != 0:
        #     comment_id = 'https://www.dcard.tw/service/api/v2/posts/' + str(id_) + '/comments?'
        #     try:
        #         time.sleep(random.uniform(10, 20))
        #         browser.get(comment_id)
        #         html_source = browser.page_source
        #         soup = BeautifulSoup(html_source, "lxml")
        #         r = soup.find('pre').text
        #         comment_info = json.loads(r)
        #
        #         for com in comment_info:
        #             try:
        #                 print(chapter['title'])
        #                 print('comment_content:', com['content'])
        #                 print('comment_like:', com['likeCount'])
        #                 comment_dict = {
        #                     "comment": com['content'],
        #                     "comment_like": com['likeCount']
        #
        #                 }
        #                 dcard_dict["reactions"].append(comment_dict)
        #             except:
        #                 print('comment deleted')
        #         result_list.append(dcard_dict)
        #     except Exception as e:
        #         print('error:', e, comment_id)
    return result_list


if __name__ == '__main__':
    result_lists = Dcard_crawl()

    # Log the results to BigQuery
    bq_dcard_metrics(today, domain, result_lists)
