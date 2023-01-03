from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from dependency.base_dependency import REQUEST_KEY
from tokenization_v2 import tokenization_data
from model.base_model import BaseResponse, DomainName
from datetime import date

tokenization_router = APIRouter()
schedule_path = '/tokenization'

start = date.today().isoformat()


@tokenization_router.post(schedule_path, response_model=BaseResponse)
def web_scraper_udnnews(request_key: str,
                        keyword: str,
                        start_date: date = start,
                        end_date: date = start,
                        domains: List[DomainName] = Query(default=[])
                        ):
    if request_key != REQUEST_KEY:
        raise HTTPException(status_code=400, detail="bad request key")
    if keyword != '':
        if start_date > end_date:
            return BaseResponse(success=False, error_msg="start_date can not bigger than end_date", result=None)

        count_dic, news_data = tokenization_data(keyword, start_date, end_date, [domain.value for domain in domains])
        return BaseResponse(success=True, error_msg='start success', dict_data=count_dic, result=None,
                            news_data=news_data)
    return BaseResponse(success=False, error_msg="keyword error", result=None)
