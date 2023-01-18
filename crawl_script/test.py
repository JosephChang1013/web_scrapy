import json
import time
import random

from typing import Any, Dict, List
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

base_url = 'https://www.dcard.tw'
options = Options()
# options.add_argument('headless')
options.add_argument('--disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--remote-debugging-port=9222')
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def dcard_crawl():
    url = 'https://www.dcard.tw/f'

    try:
        browser.get(url)
    except exceptions.InvalidSessionIdException as g:
        print(g)
    result_list: List[Dict[str, Any]] = list()
    prev_ele = None
    num = 0
    while num < 5:
        time.sleep(random.uniform(10, 15))
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "lxml")
        eles = soup.find(class_='atm_26_7ak79m w1y4fxrl').find_all("article")

        try:
            eles = eles[eles.index(prev_ele):]
        except:
            pass

        for d in eles:
            try:

                dcard_dict = {
                    "date": datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M").isoformat(),
                    "title": d.find("h2").text,
                    "link": base_url + d.find("h2").find('a')["href"],
                    "category": d.find_all(class_="atm_9s_1txwivl atm_h_1h6ojuz atm_vv_1q9ccgz atm_sq_1l2sidv atm_ks_15vqwwr atm_7l_oumlfv atm_1u2fww4_af0gpl lwxksid")[0].text,
                    "log_datetime": datetime.now().isoformat(),
                    "like_count": d.find(class_='atm_lk_i2wt44 c1jkhqx5').text,
                    "reactions": [],
                    "comment_num": d.find_all(class_='atm_9s_1txwivl atm_h_1h6ojuz atm_ll_exct8b atm_dz43bx_idpfg4 atm_1pqnrs9_gktfv atm_1dlbvfv_gktfv atm_1in2ljq_i2wt44 atm_leio7s_nmbu2e f156vo9')[-2].find('span').text
                }
                result_list.append(dcard_dict)
                result_list = json.dumps(result_list)
                result_list = dcard_crawl_content(result_list)
                result_list = json.loads(result_list)
            except Exception as e:
                print(e)
                pass

        prev_ele = eles[-1]
        js = "window.scrollTo(0, document.body.scrollHeight);"
        browser.execute_script(js)
        num += 1
        print("number", num, "scroll")

    browser.close()
    return result_list


def dcard_crawl_content(result_list):
    result_json = json.loads(result_list)
    browser.execute_script("window.open('about:blank','secondtab');")
    browser.switch_to.window("secondtab")
    try:
        for index, link in enumerate([i['link'] for i in result_json]):
            browser.get(link)
            print("Current session is {}".format(browser.session_id))
            html_source = browser.page_source
            sub_soup = BeautifulSoup(html_source, "lxml")
            time.sleep(random.uniform(8, 12))
            content = [(i.get_text()).strip() for i in
                       sub_soup.find(class_="atm_c8_exct8b atm_g3_1f4h9lt atm_7l_1u09hbr c1h57ajp").find_all("span")]
            content = ''.join(content)
            result_json[index]["content"] = content
            for c in sub_soup.find(
                    class_="atm_26_2wif97 atm_am_kb7nvz atm_9s_1txwivl atm_ar_1bp4okc atm_10vsb95_kb7nvz c18k8x7i").find_all(class_="atm_am_kb7nvz atm_ks_15vqwwr c19xyhzv"):
                comment_dict = {
                    "comment": c.find(class_="atm_vv_1btx8ck atm_w4_1hnarqo c1ehvwc9").find('span').text,
                    "comment_like": c.find(class_="atm_lk_ftgil2 atm_7l_drqgbt c8lbhra").text
                }
                result_json[index]["reactions"].append(comment_dict)

            result_list = json.dumps(result_json)
            browser.close()
            time.sleep(random.uniform(10, 15))
    except Exception as e:
        print(e)
        pass
    return result_list


if __name__ == '__main__':
    result_lists = dcard_crawl()

    with open('Dcard-articles.json', 'w', encoding='utf-8') as f:
        json.dump(result_lists, f, indent=2,
                  sort_keys=True, ensure_ascii=False)
