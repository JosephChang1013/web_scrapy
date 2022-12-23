from datetime import datetime
import random
import time
import requests

from json import dumps

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_news(num: int) -> list:
    all_news = []
    pid = ''
    while len(all_news) < num:
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
                'link': 'https://www.nownews.com' + news['postOnlyUrl'],
                'title': news['postTitle'],
                'content': news['postContent'],
                'date': datetime.strptime(news['newsDate'], "%Y-%m-%d %H:%M").strftime("%Y/%m/%d %H:%M")
            }

            all_news.append(news_data)
        pid = all_news[-1]['id']
        time.sleep(random.uniform(2, 5))
        with open('../tool/now_news.jsonl', 'w', encoding='UTF-8') as f:
            f.write('\n'.join([dumps(x, ensure_ascii=False) for x in all_news if x]))
    return all_news


if __name__ == "__main__":
    a = get_news(num=200000)
    print(a)
