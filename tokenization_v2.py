import re
from datetime import datetime, date

import jieba as jieba

from jieba import analyse
from dependency.Pagesearch import replace_comma
from tool.externalapi.bigquery_processor import big_query_execute, query_script


def is_in(full_str: str, sub_str: str) -> bool:
    if re.findall(sub_str, full_str):
        return True
    else:
        return False


def find_artcle_bykey(keyword: str, result: list) -> tuple[str, list]:
    content_data = ""
    news_data = []
    for items in result:
        for item in items:
            if is_in(replace_comma(''.join(item['content'])), keyword):
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


def tokenization_data(keyword: str,
                      start_date: date,
                      end_date: date,
                      domain: list[str],

                      ):
    query_list = query_script(start_date, end_date, domain)
    result = big_query_execute(query_list)
    content_data, news_data = find_artcle_bykey(keyword, result)

    jieba.set_dictionary('tool/dict.txt.big')
    jieba.analyse.set_stop_words('tool/stop_words.txt')
    tfidf_fre = analyse.extract_tags(content_data, topK=100, withWeight=True, allowPOS=(), withFlag=True)
    count_dic = {}
    for i in range(len(tfidf_fre)):
        count_dic[tfidf_fre[i][0]] = tfidf_fre[i][1]
    return count_dic, news_data
