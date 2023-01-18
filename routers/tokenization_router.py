from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from dependency.base_dependency import REQUEST_KEY
from crawl_script.tokenization_v2 import tokenization_data, tfidf_fre_for_bar, tfidf_fre_for_wordcloud
from model.base_model import BaseResponse, DomainName
from datetime import date

tokenization_router = APIRouter()
schedule_path = '/tokenization'

start = date.today().isoformat()


@tokenization_router.post(schedule_path, response_model=BaseResponse)
def word_tokenization(request_key: str,
                      keyword: str = None,
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

    count_dic, news_data, tfidf_fre = tokenization_data(keyword, start_date, end_date,
                                                        [domain.value for domain in domains])
    bar, wordcloid = tfidf_fre_for_bar(tfidf_fre, start_date, end_date), tfidf_fre_for_wordcloud(count_dic)
    result = bar, wordcloid
    return BaseResponse(success=True, error_msg='start success', dict_data=count_dic, result=result,
                        news_data=news_data)
