import time
import random
import requests

from datetime import datetime
from dependency.Pagesearch import today_date
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_log_metrics

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

base_url = 'https://www.udn.com'

domain = DomainName.UDNNEWS.value
today = today_date()


def get_news_list(page_num: int) -> list:
    url = "https://udn.com/api/more"

    news_list = []
    for page in range(page_num):
        channelId = 1
        cate_id = 99
        type_ = 'breaknews'
        query = f"page={page + 1}&channelId={channelId}&cate_id={cate_id}&type={type_}"
        news_list_url = url + '?' + query
        # https://udn.com/api/more?page=2&channelId=1&cate_id=99&type=breaknews
        print(news_list_url, page + 1, '/', str(page_num))

        r = requests.get(news_list_url, headers=HEADERS)
        try:
            news_data = r.json()
            news_list.extend(news_data['lists'])
            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(e)
            break

    return news_list


# url = 'https://udn.com/news/story/7324/6849920?from=udn-ch1_breaknews-1-99-news'

def start_crawl_news():
    t = get_news_list(page_num=20)

    result_list = []
    for i in t:
        result = {
            'date': datetime.strptime(i['time']['date'], "%Y-%m-%d %H:%M").isoformat(),
            'title': i['title'],
            'content': i['paragraph'],
            'link': 'https://udn.com' + i['titleLink'],
            'log_datetime': datetime.now().isoformat()
        }
        result_list.append(result)

    return result_list


if __name__ == "__main__":
    result_lists = start_crawl_news()
    print(result_lists[0])
    bq_log_metrics(today, domain, result_lists)
