import logging
from fastapi import APIRouter, HTTPException

from dependency.base_dependency import REQUEST_KEY
from crawl_script.tokenization_v2 import tokenization_data
from model.base_model import BaseResponse
from tool.externalapi.compute_processor import list_all_instances, create_an_instance
from datetime import date

ettoday_router = APIRouter()
schedule_path = '/scrapy_ettoday'
instance_name = 'web-crawl-ettoday'
tolerant = 1

start = int(date.today().strftime("%Y%m%d"))
# file_path = creat_path()
file_path = 'tool/index.jsonl'


@ettoday_router.post(schedule_path, response_model=BaseResponse)
def web_scraper_ettoday(request_key: str, keyword: str, start_date: int = start, end_date: int = start):
    if request_key != REQUEST_KEY:
        raise HTTPException(status_code=400, detail="bad request key")
    # start_crawl()
    if keyword != '':
        if start_date > end_date:
            return BaseResponse(success=False, error_msg="start_date can not bigger than end_date", result=None)
        count_dic, news_data = tokenization_data(keyword, file_path, start_date, end_date)
        return BaseResponse(success=True, error_msg='start success', dict_data=count_dic, result=None,
                            news_data=news_data)
    return BaseResponse(success=False, error_msg="keyword error", result=None)


def start_crawl():
    instances = list_all_instances(active_only=True, instance_name=instance_name)
    if len(instances) >= tolerant:
        logging.info('crawl already active')
        return
    logging.info('try activate crawl')
    create_an_instance(instance_name, 'Ettoday_selenium.py', description='crawl from web_site')
