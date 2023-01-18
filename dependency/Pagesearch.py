from datetime import timedelta, date, datetime
import re
from typing import Union, Any
from urllib.parse import urlparse
from datetime import timedelta, date
from bs4 import BeautifulSoup
import requests
from bs4.dammit import EncodingDetector


# -*- coding:utf-8 -*-

def parse(request_urls: str) -> str:
    headers = {'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/47.0.2526.106 Safari/537.36'}
    response = requests.get(request_urls, headers=headers)
    http_encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(response.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(response.text, 'lxml', from_encoding=encoding)
    text = soup.text
    text = replace_comma(text)
    print(text, sep='')
    response.close()
    return text


def replace_comma(text: str) -> str:
    # replace punctuation with space
    text = re.sub("[`\-=\[\]\\\;/~@#$%^&*_+{}|<>－【】／～￥×｛｝『』《》]+", " ", str(text))
    cop = re.compile("[^\u4e00-\u9fa5^,.?:!'()\"，。、？：！；「」（）a-zA-Z0-9 ]")
    text = cop.sub('\n', text)

    # remove extra space
    text = re.sub('\n+', '\n', text)
    text = re.sub(' +', ' ', text)

    text = [t.strip() for t in text.split('\n')]
    text = '\n'.join([t for t in text if t])

    return text.replace('\n', '')


def clean_text(text: str) -> str:
    result = []
    for i in text:
        text = text[i]['content'][2:]
        bag1 = [re.sub(r'[^\w\s]', '', j) for j in str(text)]
        bag2 = [re.sub(r'\r\n|\u3000|\n', '', j) for j in str(bag1)]
        result.append(bag2)
    text = ' '.join(map(str, result))
    return text


def creat_path(
        request_urls: str = None,
        sub_domain: str = None,
        target='target',
        num: int = None,
        extension='txt',

) -> str:
    if request_urls:
        domain = urlparse(f"{request_urls}").netloc
        path = urlparse(f"{request_urls}").path.replace('/', '')

        if path:
            file_path = f"{target}/{domain}/{sub_domain}/{path}.{extension}"
            return file_path

        if path == '':
            file_path = f"{target}/{domain}/{sub_domain}/{date.today()}.{extension}"
            return file_path

    if not request_urls:
        file_path = f"{target}/{sub_domain}/index-{num}.{extension}"
        return file_path


def date_range(start_date: date, end_date: date, include_end_date=False, mondays_only=False, time_increment=1):
    for n in range(int((end_date - start_date).days) + (1 if include_end_date else 0)):
        a_date = start_date + timedelta(n)
        if mondays_only:
            if a_date.isoweekday() != 1:
                continue
        if time_increment > 1:
            if (a_date - start_date).days % time_increment != 0:
                continue
        yield a_date


def entry_date(start_date, end_date):
    year, month, day = map(int, start_date.split('-'))
    year2, month2, day2 = map(int, end_date.split('-'))
    start_date = date(year, month, day)
    end_date = date(year2, month2, day2)
    return start_date, end_date


def today_date() -> date:
    now = datetime.now()
    today = now.date()
    return today

