import time
import random
import requests
from datetime import datetime
from json import dumps

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_news_list(page_num: int) -> list:
    base_url = "https://udn.com/api/more"

    news_list = []
    for page in range(page_num):
        channelId = 1
        cate_id = 99
        type_ = 'breaknews'
        query = f"page={page + 1}&channelId={channelId}&cate_id={cate_id}&type={type_}"
        news_list_url = base_url + '?' + query
        # https://udn.com/api/more?page=2&channelId=1&cate_id=99&type=breaknews
        print(news_list_url, page + 1, '/', str(page_num))

        r = requests.get(news_list_url, headers=HEADERS)
        try:
            news_data = r.json()
            news_list.extend(news_data['lists'])
            time.sleep(random.uniform(1, 2))
        except:
            break

    return news_list


# url = 'https://udn.com/news/story/7324/6849920?from=udn-ch1_breaknews-1-99-news'

def get_news_lists():
    t = get_news_list(page_num=1200)

    result_list = []
    for i in t:
        result = {
            'date': datetime.strptime(i['time']['date'], "%Y-%m-%d %H:%M").strftime("%Y/%m/%d %H:%M"),
            'title': i['title'],
            'content': i['paragraph'],
            'link': 'https://udn.com' + i['titleLink']}
        result_list.append(result)

    with open('../tool/udn_news.jsonl', 'w', encoding='UTF-8') as f:
        f.write('\n'.join([dumps(x, ensure_ascii=False) for x in result_list]))
    pass


if __name__ == "__main__":
    get_news_lists()
