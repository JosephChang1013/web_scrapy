import time
import requests
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from datetime import datetime, timedelta
from dependency.Pagesearch import creat_path
from dependency.base_dependency import bucket
from tool.externalapi.storage_bucket import upload_file_to_bucket, download_blob_into_memory


def start_scraper_ettoday():
    date_range = int(input('input a date of range: '))
    date_range_ago = (datetime.now() - timedelta(days=date_range))
    years = [(datetime.now() - timedelta(days=y)).year for y in range(1, date_range + 1)]
    months = [(datetime.now() - timedelta(days=m)).month for m in range(1, date_range + 1)]
    days = [(datetime.now() - timedelta(days=d)).day for d in range(1, date_range + 1)]

    for year, month, day in zip(years, months, days):
        try:
            browser = webdriver.Chrome(executable_path='./chromedriver')
            url = f"https://www.ettoday.net/news/news-list-{year}-{month}-{day}-0.htm"
            base_url = "https://www.ettoday.net"
            browser.get(url)
            time.sleep(2)

            print(f"{date_range}日前時間：", date_range_ago)

            last_height = browser.execute_script("return document.body.scrollHeight")

            go = True

            while go:
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                html_source = browser.page_source
                soup = BeautifulSoup(html_source, "lxml")

                new_height = browser.execute_script("return document.body.scrollHeight")

                # 已經到頁面底部
                if new_height == last_height:
                    print("已經到頁面最底部，程序停止")
                    break

                last_height = new_height
                time.sleep(1)
                for f in soup.find(class_="part_list_2").find_all('h3'):

                    if datetime.strptime(f.find(class_="date").text, '%Y/%m/%d %H:%M') < date_range_ago:
                        print(f"已經超出{date_range_ago}，程序停止")
                        go = False
                        break

                    else:
                        print("目前畫面最下方文章的日期時間為：", f.find_all(class_="date")[-1].text)

            # 爬取已經拓展完的頁面
            time.sleep(2)

            user_agent = UserAgent().random

            headers = {
                "user-agent": user_agent

            }
            html_source = browser.page_source

            soup = BeautifulSoup(html_source, "lxml")

            news = {"date": [],
                    "title": [],
                    "link": [],
                    "category": [],
                    "content": []
                    }

            for d in soup.find(class_="part_list_2").find_all('h3'):
                if date_range_ago in d.select(".date"):
                    pass
                else:
                    print(d.find(class_="date").text, d.find_all('a')[-1].text)
                    news["date"].append(d.find(class_="date").text)
                    news["title"].append(d.find_all('a')[-1].text)
                    news["category"].append(d.find("em").text)
                    news["link"].append(base_url + d.find_all('a')[-1]["href"])
            browser.close()
            print(f'start crawl content,total: {len(news["title"])}')
            for i, url in enumerate(news['link']):
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                content = [(i.get_text()).strip() for i in soup.select("div.story > p ")]
                print(f"start crawling content {news['date'][i]} {i}/{len(news['link'])}")
                news["content"].append(content)
                time.sleep(1)
            print(f'start creating dataframe')
            df_news = pd.DataFrame(news)
            file_path = creat_path(
                base_url,
                sub_domain='content',
                target='ETtoday',
                extension='jsonl'
            )
            print(f'start upload to storage')
            blob = bucket.blob(file_path)

            if blob.exists():
                data = download_blob_into_memory(file_path).decode("utf-8")
                df_old = pd.read_json(data, lines=True)
                df_old = pd.concat([df_old, df_news],
                                   verify_integrity=True,
                                   ignore_index=True)
                data_json = df_old.to_json(lines=True, orient='records', force_ascii=False, date_format='iso')
                upload_file_to_bucket(data_json, file_path)
                print("files exist updating")
                continue

            if not blob.exists():
                data_json = df_news.to_json(lines=True, orient='records', force_ascii=False, date_format='iso')
                upload_file_to_bucket(data_json, file_path)
                print("files not exist creating")
                continue
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    start_scraper_ettoday()
