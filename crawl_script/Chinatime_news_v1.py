import random
import time
import requests

from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dependency.Pagesearch import today_date
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_log_metrics

# Define the base URL and the target domain
base_url = "https://www.chinatimes.com"
domain = DomainName.CHINATIME.value
today = today_date()


def start_crawl_chinatime():
    result_list: List[Dict[str, Any]] = list()
    for page in range(1, 11):

        # Define the URL for the current page and generate a random user agent
        url = f'https://www.chinatimes.com/realtimenews/?page={page}&chdtv'
        user_agent = UserAgent().random

        headers = {
            "user-agent": user_agent

        }

        rep = requests.get(url, headers=headers)
        soup = BeautifulSoup(rep.text, "lxml")

        # Loop through the articles on the current page and extract the relevant information
        for d in soup.find_all(class_="articlebox-compact"):
            while True:
                try:
                    # Extract the date, title, link, category, and content of the current article
                    news = {"date": datetime.strptime(d.find('time')['datetime'], "%Y-%m-%d %H:%M").isoformat(),
                            "title": d.find('h3', class_='title').text,
                            "link": base_url + d.find('h3')('a')[-1]['href'],
                            "category": d.find('div', class_='category').text,
                            "log_datetime": datetime.now().isoformat()
                            }

                    # Send an HTTP request to the article page and parse the HTML using BeautifulSoup
                    rep = requests.get(news['link'], headers=headers)
                    sub_soup = BeautifulSoup(rep.text, 'lxml')

                    # Extract the content of the article
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

    # Log the results to BigQuery
    bq_log_metrics(today, domain, result_lists)
