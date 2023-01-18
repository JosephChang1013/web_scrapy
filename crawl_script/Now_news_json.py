import random
import time
import requests

from typing import List, Dict, Any
from datetime import datetime
from dependency.Pagesearch import today_date
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_log_metrics

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

base_url = 'https://www.nownews.com'
domain = DomainName.NOWNEWS.value
today = today_date()


def get_news(num: int):
    result_list: List[Dict[str, Any]] = list()
    pid = ''
    while len(result_list) < num:
        url = f'https://www.nownews.com/nn-client/api/v1/cat/breaking/?pid={pid}'
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            print(f'Requests Error: {r.status_code}')
            break
        data = r.json()
        news_list = data['data']['newsList']
        for news in news_list:
            news_data = {
                'id': news['id'],
                'title': news['postTitle'],
                'link': 'https://www.nownews.com' + news['postOnlyUrl'],
                'content': news['postContent'],
                'date': datetime.strptime(news['newsDate'], "%Y-%m-%d %H:%M").isoformat(),
                'log_datetime': datetime.now().isoformat()

            }

            result_list.append(news_data)
        pid = result_list[-1]['id']
        time.sleep(random.uniform(2, 5))

    return result_list


if __name__ == "__main__":
    result_lists = get_news(num=500)
    bq_log_metrics(today, domain, result_lists)
