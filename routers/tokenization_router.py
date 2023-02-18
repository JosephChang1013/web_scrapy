from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from dependency.base_dependency import REQUEST_KEY
from crawl_script.tokenization_v2 import tokenization_data
from model.base_model import BaseResponse, DomainName
from datetime import date

tokenization_router = APIRouter()
schedule_path = '/tokenization'

start = date.today().isoformat()
topk_num = 20


@tokenization_router.post(schedule_path, response_model=BaseResponse)
def word_tokenization(request_key: str,
                      keyword: str,
                      topk: int = topk_num,
                      start_date: date = start,
                      end_date: date = start,
                      domains: List[DomainName] = Query(default=[])
                      ):
    if request_key != REQUEST_KEY:
        raise HTTPException(status_code=400, detail="bad request key")

    if not start_date and end_date:
        return BaseResponse(success=False, error_msg="date must key in", result=None)

    if start_date > end_date:
        return BaseResponse(success=False, error_msg="start_date can not bigger than end_date", result=None)

    if keyword:
        count_dic, json_data, tfidf_fre = tokenization_data(keyword, topk, start_date, end_date,
                                                            [domain.value for domain in domains])

        return BaseResponse(success=True, error_msg='start success', dict_data=count_dic, result=None,
                            json_data=json_data)
    return BaseResponse(success=False, error_msg="keyword must key in", result=None)
