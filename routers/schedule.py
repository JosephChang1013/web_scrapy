import logging
from fastapi import APIRouter, HTTPException
from dependency.base_dependency import REQUEST_KEY
from tool.externalapi.compute_processor import list_all_instances, create_an_instance

schedule_router = APIRouter()
schedule_path = '/schedule'
instance_name = 'web-crawl'
tolerant = 1


@schedule_router.post(schedule_path)
def web_scraper_schedule(request_key: str):
    if request_key != REQUEST_KEY:
        raise HTTPException(status_code=400, detail="bad schedule key")
    start_crawl()
    return 'start success'


def start_crawl():
    instances = list_all_instances(active_only=True, instance_name=instance_name)
    if len(instances) >= tolerant:
        logging.info('crawl already active')
        return
    logging.info('try activate crawl')
    create_an_instance(instance_name, 'main_crawl.py', description='crawl from web_site')
