import json
import re
from datetime import datetime

import jieba as jieba

from jieba import analyse
from dependency.Pagesearch import replace_comma


def is_in(full_str, sub_str) -> bool:
    if re.findall(sub_str, full_str):
        return True
    else:
        return False


def find_artcle_bykey(keyword: str, result: list, start_date, end_date) -> tuple[str, list]:
    content_data = ""
    news_data = []
    for item in result:
        if is_in(replace_comma(''.join(item['content'])), keyword):
            try:
                art_date = int(datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y%m%d"))
            except:
                art_date = int(datetime.strptime(item['date'], "%Y/%m/%d %H:%M").strftime("%Y%m%d"))

            if art_date not in range(start_date, end_date):
                continue
            try:
                result_dict = {'title': item['title'],
                               'date': item['date'],
                               'link': item['link'],
                               'category': item['category'],
                               'content': item['content']}
            except:
                result_dict = {'title': item['title'],
                               'date': item['date'],
                               'link': item['link'],
                               'content': item['content']}

            content_data += str(result_dict['content'])
            news_data.append(result_dict)
            continue

    return content_data, news_data


def load_text_jsonl(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        json_list = list(f)
    result = []
    for json_str in json_list:
        data = json.loads(json_str)
        result.append(data)
    return result


def tokenization_data(keyword, file_path, start_date, end_date):
    result = load_text_jsonl(file_path=file_path)
    content_data, news_data = find_artcle_bykey(keyword, result, start_date, end_date)

    jieba.set_dictionary('tool/dict.txt.big')
    jieba.analyse.set_stop_words('tool/stop_words.txt')
    tfidf_fre = analyse.extract_tags(content_data, topK=100, withWeight=True, allowPOS=(), withFlag=True)
    count_dic = {}
    for i in range(len(tfidf_fre)):
        count_dic[tfidf_fre[i][0]] = tfidf_fre[i][1]
    return count_dic, news_data
