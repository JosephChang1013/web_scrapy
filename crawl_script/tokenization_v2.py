import re
import jieba as jieba

from datetime import date

from jieba import analyse
from dependency.Pagesearch import replace_comma
from tool.externalapi.bigquery_processor import big_query_execute, query_script


def is_in(full_str: str, sub_str: str) -> bool:
    if re.findall(sub_str, full_str):
        return True
    else:
        return False


def find_artcle_bykey(sentence: list, result: list) -> tuple[str, list]:
    content_data = ""
    json_data = []
    for items in result:
        for item in items:
            for keyword in sentence:
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
                    json_data.append(result_dict)
                    continue

    return content_data, json_data


def tokenization_data(keyword: str,
                      topk: int,
                      start_date: date,
                      end_date: date,
                      domain: list[str],

                      ):
    query_list = query_script(start_date, end_date, domain)
    result = big_query_execute(query_list)

    sentence = tokenization_keyword(keyword)
    content_data, json_data = find_artcle_bykey(sentence, result)

    jieba.set_dictionary('tool/dict.txt.big')
    jieba.analyse.set_stop_words('tool/stop_words.txt')
    tfidf_fre = analyse.extract_tags(content_data, topK=topk, withWeight=True, allowPOS=(), withFlag=True)

    count_dic = {}
    for i in range(len(tfidf_fre)):
        count_dic[tfidf_fre[i][0]] = tfidf_fre[i][1]
    return count_dic, json_data, tfidf_fre


def tokenization_keyword(keyword: str) -> list:
    jieba.set_dictionary('tool/dict.txt.big')
    jieba.analyse.set_stop_words('tool/stop_words.txt')
    sentence = jieba.cut(keyword, cut_all=False)
    return sentence

# 長條圖
#
# def tfidf_fre_for_bar(tfidf_fre: list,
#                       start_date: date,
#                       end_date: date,
#                       ):
#     font_spec = font_manager.FontProperties(fname="tool/NotoSerifTC[wght].ttf")
#     # fig_spec = plt.figure(figsize=(10, 6), dpi=100)
#
#     offset_width = 0.4
#
#     x = []
#     h = []
#
#     for i in range(len(tfidf_fre)):
#         x.append(tfidf_fre[i][0])
#         h.append(tfidf_fre[i][1])
#
#     plt.bar(x, h, width=offset_width)
#     plt.legend(prop=font_spec)
#     plt.grid()
#     plt.xlabel("Keyword", fontproperties=font_spec, size=12)
#     plt.ylabel("Weight", fontproperties=font_spec, size=12)
#     plt.title(f"Volume of {start_date} to {end_date}", fontproperties=font_spec, size=20)
#     plt.xticks(x, fontproperties=font_spec, rotation=0)
#     return plt.show()


# 文字雲
#
# def tfidf_fre_for_wordcloud(count_dic: dict):
#     myWordClode = WordCloud(
#         width=1800,
#         height=1200,
#         background_color="black",
#         colormap="Dark2",
#         font_path='tool/SourceHanSansTW-Regular.otf'
#
#     ).fit_words(count_dic)
#     plt.figure(figsize=(8, 6), dpi=100)
#     plt.imshow(myWordClode)
#     plt.axis("off")
#     return plt.show()
