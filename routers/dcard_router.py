import logging

from fastapi import APIRouter, HTTPException
from dependency.base_dependency import REQUEST_KEY
from tool.externalapi.compute_processor import list_all_instances, create_an_instance

dcard_router = APIRouter()
schedule_path = '/scrapy_dcard'
instance_name = 'web-crawl-dcard'
tolerant = 1


@dcard_router.post(schedule_path)
def web_scraper_dcard(request_key: str):
    if request_key != REQUEST_KEY:
        raise HTTPException(status_code=400, detail="bad request key")
    start_crawl_dcard()
    return 'start success'


def start_crawl_dcard():
    instances = list_all_instances(active_only=True, instance_name=instance_name)
    if len(instances) >= tolerant:
        logging.info('crawl already active')
        return
    logging.info('try activate crawl')
    create_an_instance(instance_name, 'Dcard_v1.py', description='crawl from web_site')
