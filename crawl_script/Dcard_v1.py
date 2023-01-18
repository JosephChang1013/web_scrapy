import time

from typing import Any, Dict, List
from bs4 import BeautifulSoup
from datetime import datetime
from dependency.Pagesearch import today_date
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_dcard_metrics

today = today_date()
base_url = 'https://www.dcard.tw'
domain = DomainName.DCARD.value


def dcard_crawl():
    while True:
        result_list: List[Dict[str, Any]] = list()
        url = 'https://www.dcard.tw/f'

        options = Options()
        # options.add_argument('headless')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Current session is {}".format(browser.session_id))
        try:
            browser.get(url)
        except exceptions.InvalidSessionIdException as g:
            print(g)
            break
        time.sleep(2)

        try:
            last_height = browser.execute_script("return document.body.scrollHeight")
            num = 0
            while num < 5:
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                browser.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
                time.sleep(3)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                html_source = browser.page_source
                soup = BeautifulSoup(html_source, "lxml")
                new_height = browser.execute_script("return document.body.scrollHeight")
                # 已經到頁面底部
                if new_height == last_height:
                    print("已經到頁面最底部，程序停止")
                    break
                last_height = new_height
                print(num + 1, "目前畫面最下方的文章為：",
                      soup.find(class_='atm_26_7ak79m w1y4fxrl').find_all("article")[-1].find("h2").text)
                num += 1
            print('page extract completed,start crawling')
            time.sleep(5)

            html_source = browser.page_source

            browser.close()
            print("Session {} closed".format(browser.session_id))

            soup = BeautifulSoup(html_source, "lxml")
            for d in soup.find(class_='atm_26_7ak79m w1y4fxrl').find_all("article"):
                dcard_dict = {
                    "date": datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").isoformat(),
                    "title": d.find("h2").text,
                    "link": base_url + d.find("h2").find('a')["href"],
                    "category": d.find_all(
                        class_="atm_9s_1txwivl atm_h_1h6ojuz atm_vv_1q9ccgz atm_sq_1l2sidv atm_ks_15vqwwr atm_7l_oumlfv atm_1u2fww4_af0gpl lwxksid")[
                        0].text,
                    "log_datetime": datetime.now().isoformat(),
                    "like_count": d.find(class_='atm_lk_i2wt44 c1jkhqx5').text,
                    "reactions": [],
                    "comment_num": d.find_all(
                        class_='atm_9s_1txwivl atm_h_1h6ojuz atm_ll_exct8b atm_dz43bx_idpfg4 atm_1pqnrs9_gktfv atm_1dlbvfv_gktfv atm_1in2ljq_i2wt44 atm_leio7s_nmbu2e f156vo9')[
                        -2].find(
                        'span').text
                }
                browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                try:
                    browser.get(dcard_dict['link'])
                    print("Current session is {}".format(browser.session_id))
                except exceptions.InvalidSessionIdException as g:
                    print(g)
                    break

                html_source = browser.page_source
                sub_soup = BeautifulSoup(html_source, "lxml")
                time.sleep(5)
                content = [(i.get_text()).strip() for i in sub_soup.find(class_="atm_c8_exct8b atm_g3_1f4h9lt atm_7l_1u09hbr c1h57ajp").find_all("span")]
                content = ''.join(content)
                dcard_dict["content"] = content
                for c in sub_soup.find(class_="atm_26_2wif97 atm_am_kb7nvz atm_9s_1txwivl atm_ar_1bp4okc atm_10vsb95_kb7nvz c18k8x7i").find_all(
                        class_="atm_am_kb7nvz atm_ks_15vqwwr c19xyhzv"):
                    comment_dict = {"comment": c.find(class_="atm_vv_1btx8ck atm_w4_1hnarqo c1ehvwc9").find('span').text,
                                    "comment_like": c.find(class_="atm_lk_ftgil2 atm_7l_drqgbt c8lbhra").text}
                    dcard_dict["reactions"].append(comment_dict)
                result_list.append(dcard_dict)
                time.sleep(5)
                browser.close()
                print("Session {} closed".format(browser.session_id))

        except Exception as e:
            print("Error", e)

        break
    return result_list


#     for chapter in chapters:
#         time.sleep(random.randint(2, 6))
#         print('title:', chapter['title'])
#         print('content:', chapter['excerpt'])
#         print('comment:', chapter['commentCount'])
#         print('like:', chapter['likeCount'])
#         dcard_dict = {
#             "title": chapter['title'],
#             "date": chapter['createdAt'],
#             "article_content": chapter['excerpt'],
#             "comment_num": chapter['commentCount'],
#             "like_count": chapter['likeCount'],
#             "comment_content": [],
#             "comment_like": [],
#             "log_datetime": datetime.now().isoformat()
#         }
#         id_ = chapter['id']
#         if chapter['commentCount'] != 0:
#             comment_id = 'https://www.dcard.tw/service/api/v2/posts/' + str(id_) + '/comments?'
#             try:
#                 comment_info = requests.get(comment_id, headers=headers).json()
#                 for com in comment_info:
#                     try:
#                         print(chapter['title'])
#                         print('comment_content:', com['content'])
#                         print('comment_like:', com['likeCount'])
#
#                         dcard_dict["comment_content"].append(com['content'])
#                         dcard_dict["comment_like"].append(com['likeCCount'])
#                     except:
#                         print('comment deleted')
#             except:
#                 print('json error：', comment_id)
#
#         result_list.append(dcard_dict)
#         print('crawl finished')
#         break
#
# return result_list


if __name__ == '__main__':
    result_lists = dcard_crawl()
    print('saving to BQ')
    print(result_lists[0])
    bq_dcard_metrics(today, domain, result_lists)
    print('accompleted job')
