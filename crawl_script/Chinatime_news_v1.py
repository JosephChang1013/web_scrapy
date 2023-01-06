import random
import time
import requests

from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dependency.Pagesearch import find_domain, today_date
from tool.externalapi.bigquery_processor import bq_log_metrics

base_url = "https://www.chinatimes.com"
domain = find_domain(base_url)
today = today_date()


def start_crawl_chinatime():
    result_list: List[Dict[str, Any]] = list()
    for page in range(1, 11):
        url = f'https://www.chinatimes.com/realtimenews/?page={page}&chdtv'
        user_agent = UserAgent().random

        headers = {
            "user-agent": user_agent

        }

        rep = requests.get(url, headers=headers)
        soup = BeautifulSoup(rep.text, "lxml")
        for d in soup.find_all(class_="articlebox-compact"):
            while True:
                try:
                    news = {"date": datetime.strptime(d.find('time')['datetime'], "%Y-%m-%d %H:%M").isoformat(),
                            "title": d.find('h3', class_='title').text,
                            "link": base_url + d.find('h3')('a')[-1]['href'],
                            "category": d.find('div', class_='category').text,
                            "log_datetime": datetime.now().isoformat()
                            }
                    rep = requests.get(news['link'], headers=headers)
                    sub_soup = BeautifulSoup(rep.text, 'lxml')
                    content = [(i.get_text()).strip() for i in sub_soup.select("div.article-body > p ")]
                    content = ''.join(content)
                    news["content"] = content
                    result_list.append(news)

                except Exception as e:
                    print("Error Occur:", e)
                    time.sleep(random.uniform(5, 8))
                    print("okey time to retry!")
                    continue

                break
    return result_list


if __name__ == "__main__":
    result_lists = start_crawl_chinatime()
    print(result_lists[0])
    bq_log_metrics(today, domain, result_lists)

