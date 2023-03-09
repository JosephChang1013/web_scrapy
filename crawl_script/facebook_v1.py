import time
import traceback
import datetime

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
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


def facebook_crawl(urls: list, date_range: int) -> List[Dict[str, Any]]:
    result_list = []
    date_range_ago = datetime.today() - timedelta(days=date_range)
    for url in urls:
        options = Options()
        options.add_argument('headless')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1920x1080')
        options.add_argument("--start-maximized")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')  # 禁用共享內存
        options.add_argument("--disable-extensions")
        options.add_argument('--remote-debugging-port=9222')
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Current session is {}".format(browser.session_id))
        try:
            browser.get(url)
            print(url)
        except exceptions.InvalidSessionIdException as g:
            print('session error: ', g)
        time.sleep(10)
        print(f"{date_range}日前時間：", date_range_ago)
        try:
            last_height = browser.execute_script("return document.body.scrollHeight")
            while True:
                html_source = browser.page_source
                soup = BeautifulSoup(html_source, "lxml")
                try:
                    click_more_content(browser)

                    for i in range(5):
                        click_more_comment(browser)


                except:
                    print(traceback.format_exc())
                    pass
                time.sleep(5)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                new_height = browser.execute_script("return document.body.scrollHeight")
                try:

                    last_date = soup.find_all('a',
                                              class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm')[
                        -1].text
                    last_date = post_date_transfer(last_date)
                    print("current window bottom article date: ", last_date)
                except:
                    print('no date data fnd')
                    break

                if new_height == last_height:
                    print("no more article,shut down")
                    break
                last_height = new_height
                if last_date < date_range_ago:
                    print(f'reach {date_range_ago} process stop')
                    break

            # 爬取已經拓展完的頁面
            print('start crawler!!')
            html_extend = browser.page_source
            soup_extend = BeautifulSoup(html_extend, "lxml")

            divs = soup_extend.find_all('div', class_='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')
            time.sleep(5)
            browser.close()
            for div in divs:
                try:
                    title = div.find('h2', class_='x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x1gslohp x1yc453h').text
                    post_date = div.find('a',
                                         class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm').text
                    post_date = post_date_transfer(post_date).isoformat()

                    try:
                        content = div.find('div', class_='x1iorvi4 x1pi30zi x1swvt13 x1l90r2v').text
                    except:
                        content = None
                        pass
                    try:
                        like_count = div.find('span', class_='xrbpyxo x6ikm8r x10wlt62 xlyipyv x1exxlbk').find(
                            'span', class_='x1e558r4').text
                        if like_count == "":
                            like_count = 1
                    except:
                        like_count = None
                        pass

                    try:
                        comment_count = div.find_all('div',
                                                     class_='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x2lah0s x193iq5w xeuugli xg83lxy x1h0ha7o x10b6aqq x1yrsyyn')[
                            0].find(
                            'span',
                            class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa').text
                    except:
                        comment_count = None
                        pass

                    fb_post_dict = {
                        "title": title,
                        "date": post_date,
                        "content": content,
                        "like_count": like_count,
                        "comment_count": comment_count,
                        "comment_reaction": [],
                        "log_datetime": datetime.now().isoformat()
                    }
                    if comment_count != 0:
                        div_comment = div.find_all('div', class_='x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi')
                        for d in div_comment:

                            try:
                                comment_name = d.find(
                                    class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa x1s688f xzsf02u').text
                            except:
                                comment_name = None
                                pass

                            try:
                                comment_text = d.find('div',
                                                      class_='x11i5rnm xat24cr x1mh8g0r x1vvkbs xdj266r').text
                            except:
                                comment_text = None
                                pass

                            try:
                                comment_date = d.find('a',
                                                      class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1fcty0u').find(
                                    class_='x4k7w5x x1h91t0o x1h9r5lt xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j x1jfb8zj').text


                            except:
                                comment_date = None
                                pass

                            fb_comment_dict = {
                                "comment_name": comment_name,
                                "comment_date": comment_date_transfer(comment_date).isoformat(),
                                "comment_text": comment_text,
                            }
                            fb_post_dict["comment_reaction"].append(fb_comment_dict)
                    else:
                        fb_comment_dict = {
                            "comment_name": None,
                            "comment_date": None,
                            "comment_text": None,

                        }
                        fb_post_dict["comment_reaction"].append(fb_comment_dict)

                    result_list.append(fb_post_dict)

                except:
                    print(traceback.format_exc())
                    pass

                time.sleep(5)


        except Exception:
            print(traceback.format_exc())
    return result_list


def click_more_content(browser):
    more_btn = browser.find_elements(By.XPATH,
                                     '//div[@class="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f"]')
    if len(more_btn) > 0:
        count = 0
        for i in more_btn:

            # 創建一個 ActionChains 物件，用於模擬滑鼠操作
            action = ActionChains(browser)

            # 嘗試模擬滑鼠移動到元素位置並點擊
            try:
                action.move_to_element(i).click.perform()
                count += 1

            # 如果上面的操作失敗，嘗試使用 JavaScript 模擬點擊
            except:
                try:
                    browser.execute_script("arguments[0].click();", i)
                    count += 1
                except:
                    continue

        # 如果有元素點擊成功但還有元素沒有被點擊成功，輸出錯誤訊息
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


def post_date_transfer(input_date: str) -> date:
    if 'm' in input_date:
        mins = int(input_date.split('m')[0])
        post_date = (datetime.now() - timedelta(minutes=mins))
        return post_date

    if 'h' in input_date:
        hour = int(input_date.split('h')[0])
        post_date = (datetime.now() - timedelta(hours=hour))
        return post_date

    elif 'd' in input_date:
        day = int(input_date.split('d')[0])
        post_date = (datetime.today() - timedelta(days=day))
        return post_date

    else:
        try:
            now = datetime.now()
            year = now.year
            post_date = datetime.strptime(input_date + str(year), '%B %d%Y')
            return post_date

        except ValueError:
            try:
                now = datetime.now()
                year = now.year
                post_date = datetime.strptime(input_date + str(year), '%B %d at %I:%M %p%Y')
                return post_date

            except ValueError:
                try:
                    post_date = datetime.strptime(input_date, '%B %d, %Y')
                    return post_date
                except ValueError:
                    try:
                        post_date = datetime.strptime(input_date, '%d %B at %H:%M%Y')
                        return post_date
                    except ValueError:
                        now = datetime.now()
                        year = now.year
                        post_date = datetime.strptime(input_date + str(year), '%d %B at %H:%M%Y')
                        return post_date


def comment_date_transfer(input_date: str):
    if 'm' in input_date:
        mins = int(input_date.split('m')[0])
        post_date = (datetime.now() - timedelta(minutes=mins))
        return post_date
    if 'h' in input_date:
        hour = int(input_date.split('h')[0])
        post_date = datetime.now() - timedelta(hours=hour)
        return post_date
    if 'd' in input_date:
        day = int(input_date.split('d')[0])
        post_date = (datetime.now() - timedelta(days=day))
        return post_date
    if 'w' in input_date:
        week = int(input_date.split('w')[0])
        post_date = (datetime.now() - timedelta(weeks=week))
        return post_date
    if 'y' in input_date:
        year = int(input_date.split('y')[0])
        post_date = (datetime.now() - relativedelta(years=year))
        return post_date


if __name__ == '__main__':
    url_list = ['https://www.facebook.com/ChubbLifeTaiwan',  # 安達人壽
                'https://www.facebook.com/TGLlife',  # 全球人壽
                'https://www.facebook.com/Cathaylife',  # 國泰人壽
                'https://www.facebook.com/NanShanLifeInsurance',  # 南山人壽
                'https://www.facebook.com/healthnews.tw'  # 健康醫療網
                ]
    date_range = 30
    result_lists = facebook_crawl(url_list, date_range)
    print(result_lists[0])
    bq_facebook_metrics(today, domain, result_lists)
