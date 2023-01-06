from json import dumps
import requests
from dependency.Pagesearch import creat_path
from tool.externalapi.storage_bucket import upload_file_to_bucket


def start_crawling():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    url = 'https://data.gov.tw/api/front/dataset/list'
    file_path = creat_path(url, target='govdata', sub_domain='content', extension='jsonl')
    result_list = []
    for i in range(1, 1000):
        data = {
            "bool": [],
            "filter": [],
            "page_num": i,
            "page_limit": 1000,
            "tids": [],
            "sort": "metadata_changed.date_desc"

        }
        resp = requests.post(url, json=data, headers=headers).json()
        search_result = resp["payload"]["search_result"]

        if not search_result:
            break

        result_list.extend(search_result)

    upload_file_to_bucket('\n'.join([dumps(x, ensure_ascii=False) for x in result_list]), file_path)


if __name__ == '__main__':
    start_crawling()
