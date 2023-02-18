import time
import traceback

from typing import Any, Dict, List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from dependency.Pagesearch import today_date
from model.base_model import DomainName
from tool.externalapi.bigquery_processor import bq_facebook_metrics

today = today_date()
domain = DomainName.FACEBOOK.value


def facebook_crawl(urls: list) -> List[Dict[str, Any]]:
    result_list = []
    for url in urls:
        user_agent = UserAgent().random
        options = Options()
        # options.add_argument('headless')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--start-maximized")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        # options.add_argument('--user-agent=%s' % user_agent)
        options.add_argument('--remote-debugging-port=9222')
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Current session is {}".format(browser.session_id))
        try:
            browser.get(url)
            print(url)
        except exceptions.InvalidSessionIdException as g:
            print('session error: ', g)
        time.sleep(5)
        try:
            last_height = browser.execute_script("return document.body.scrollHeight")
            while True:
                html_source = browser.page_source
                soup = BeautifulSoup(html_source, "lxml")
                try:
                    click_more_content(browser)
                    getBack(browser)

                    for i in range(5):
                        click_more_comment(browser)
                        getBack(browser)

                except:
                    print(traceback.format_exc())
                    pass
                time.sleep(3)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = browser.execute_script("return document.body.scrollHeight")
                last_date = soup.find_all('a',
                                          class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm')[
                    -1].text
                print("current window bottom article date: ", last_date)
                if new_height == last_height:
                    print("no more article,shut down")
                    break
                last_height = new_height

            while True:
                html_extend = browser.page_source
                soup_extend = BeautifulSoup(html_extend, "lxml")

                divs = soup_extend.find_all('div', class_='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')
                time.sleep(1)

                browser.close()
                for div in divs:
                    try:
                        title = div.find('h2', class_='x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x1gslohp x1yc453h').text
                        post_date = div.find('a',
                                             class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm').text
                        try:
                            content = div.find('div', class_='x1iorvi4 x1pi30zi x1swvt13 x1l90r2v').text
                        except:
                            content = 'No data'
                            pass
                        try:
                            like_count = div.find('span', class_='xrbpyxo x6ikm8r x10wlt62 xlyipyv x1exxlbk').find(
                                'span', class_='x1e558r4').text
                            if like_count == "":
                                like_count = 1
                        except:
                            like_count = 'No data'
                            pass

                        # try:
                        #     anger_count = ''
                        #     if anger_count == "":
                        #         anger_count = 1
                        # except:
                        #     anger_count = 'No data'
                        #     pass
                        # try:
                        #     haha_count = ''
                        #     if haha_count == "":
                        #         haha_count = 1
                        # except:
                        #     haha_count = 'No data'
                        #     pass
                        # try:
                        #     love_count = ''
                        #     if love_count == "":
                        #         love_count = 1
                        # except:
                        #     love_count = 'No data'
                        #     pass
                        # try:
                        #     sorry_count = ''
                        #     if sorry_count == "":
                        #         sorry_count = 1
                        # except:
                        #     sorry_count = 'No data'
                        #     pass
                        # try:
                        #     wow_count = ''
                        #     if wow_count == "":
                        #         wow_count = 1
                        # except:
                        #     wow_count = 'No data'
                        #     pass
                        try:
                            comment_count = div.find('div',
                                                     class_='x1i10hfl x1qjc9v5 xjqpnuy xa49m3k xqeqjp1 x2hbi6w x1ypdohk xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x1hl2dhg xggy1nq x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz xjyslct xjbqb8w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1heor9g xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1ja2u2z xt0b8zv').find(
                                'span',
                                class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa').text
                        except:
                            comment_count = 'No data'
                            pass
                        try:
                            share_count = div.find_all('div',
                                                       class_='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x2lah0s x193iq5w xeuugli xsyo7zv x16hj40l x10b6aqq x1yrsyyn')[
                                -1].find(
                                'span',
                                class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa').text
                        except:
                            share_count = 'No data'
                            pass

                        fb_post_dict = {
                            "post_name": title,
                            "post_date": post_date,
                            "content": content,
                            "like_count": like_count,
                            # "anger_count": anger_count,
                            # "haha_count": haha_count,
                            # "love_count": love_count,
                            # "sorry_count": sorry_count,
                            # "wow_count": wow_count,
                            "comment_count": comment_count,
                            "share_count": share_count,
                            "comment_reaction": [],
                        }
                        if fb_post_dict["comment_count"] == 'No data':
                            fb_comment_dict = {
                                "comment_name": 'No data',
                                "comment_date": 'No data',
                                "comment_text": 'No data',
                                "comment_like_count": 'No data'
                            }
                            fb_post_dict["comment_reaction"].append(fb_comment_dict)
                            result_list.append(fb_post_dict)
                            continue
                        div_comment = div.find_all('div', class_='x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi')

                        for d in div_comment:

                            try:
                                comment_name = d.find(
                                    class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa x1s688f xzsf02u').text
                            except:
                                comment_name = 'No data'
                                pass

                            try:
                                comment_like_count = d.find('span',
                                                            class_='x4k7w5x x1h91t0o x1h9r5lt xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j x1jfb8zj').text
                                if comment_like_count == "":
                                    comment_like_count = 1

                            except:
                                comment_like_count = 'No data'
                                pass

                            try:
                                comment_text = d.find('div',
                                                      class_='x11i5rnm xat24cr x1mh8g0r x1vvkbs xdj266r').text
                            except:
                                comment_text = 'No data'
                                pass

                            try:
                                comment_date = d.find('a',
                                                      class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1fcty0u').find(
                                    class_='x4k7w5x x1h91t0o x1h9r5lt xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j x1jfb8zj').text
                            except:
                                comment_date = 'No data'
                                pass

                            fb_comment_dict = {
                                "comment_name": comment_name,
                                "comment_date": comment_date,
                                "comment_text": comment_text,
                                "comment_like_count": comment_like_count
                            }
                            if fb_comment_dict["comment_date"] == fb_comment_dict["comment_like_count"]:
                                fb_comment_dict["comment_like_count"] = "no data"
                            fb_post_dict["comment_reaction"].append(fb_comment_dict)

                        result_list.append(fb_post_dict)

                    except:
                        print(traceback.format_exc())
                        pass

                time.sleep(2)


        except Exception:
            print(traceback.format_exc())
    return result_list


def click_more_content(browser):
    more_btn = browser.find_elements(By.XPATH,
                                     '//div[@class="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f"]')
    if len(more_btn) > 0:
        count = 0
        for i in more_btn:
            action = ActionChains(browser)
            try:
                action.move_to_element(i).click.perform()
                count += 1
            except:
                try:
                    browser.execute_script("arguments[0].click();", i)
                    count += 1
                except:
                    continue
        if len(more_btn) - count > 0:
            print('moreComment issue:', len(more_btn) - count)
        time.sleep(1)
    else:
        pass


def click_more_comment(browser):
    more_btn = browser.find_elements(By.XPATH,
                                     '//span[@class="x78zum5 x1w0mnb xeuugli"]')
    if len(more_btn) > 0:
        count = 0
        for i in more_btn:
            action = ActionChains(browser)
            try:
                action.move_to_element(i).click.perform()
                count += 1
            except:
                try:
                    browser.execute_script("arguments[0].click();", i)
                    count += 1
                except:
                    continue
        if len(more_btn) - count > 0:
            print('moreComment issue:', len(more_btn) - count)
        time.sleep(1)
    else:
        pass


def getBack(browser):
    if not browser.current_url.endswith('reviews'):
        print('redirected!!!')
        browser.back()
        print('got back!!!')


if __name__ == '__main__':
    url_list = ['https://www.facebook.com/ChubbLifeTaiwan',
                ]

    result_lists = facebook_crawl(url_list)
    bq_facebook_metrics(today, domain, result_lists)
