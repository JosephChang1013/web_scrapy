# import logging
# import traceback
#
# from datetime import datetime
# from fastapi import APIRouter, Response, status
# from dependency.base_dependency import REQUEST_KEY, bucket_name, bucket
# from model.base_model import BaseResponse, blob_metadata
# from dependency.Pagesearch import parse, creat_path
# from tool.externalapi.storage_bucket import upload_file_to_bucket, download_blob_into_memory
#
# scrapy_router = APIRouter()
# scraper_path = '/scraper'
#
#
# @scrapy_router.get(scraper_path, response_model=BaseResponse)
# async def web_scraper(
#         request_key: str,
#         response: Response,
#         request_urls: str,
# ):
#     try:
#
#         if request_key != REQUEST_KEY:
#             response.status_code = status.HTTP_400_BAD_REQUEST
#             return BaseResponse(success=False, error_msg='request_key error', result=None)
#
#         if not request_urls:
#             response.status_code = status.HTTP_400_BAD_REQUEST
#             return BaseResponse(success=False, error_msg='request_url error', result=None)
#         if request_urls:
#             file_path = creat_path(request_urls, sub_domain='scrapy')
#             blob = bucket.blob(file_path)
#             if blob.exists():
#                 if (datetime.utcnow().replace(tzinfo=None) - blob_metadata(bucket_name, blob)).days > 30:
#                     success = parse(request_urls)
#                     upload_file_to_bucket(success, file_path)
#                     return BaseResponse(success=True, error_msg='', result=success)
#                 if (datetime.now().replace(tzinfo=None) - blob_metadata(bucket_name, blob)).days < 30:
#                     success = download_blob_into_memory(file_path)
#                     success = success.decode("utf-8")
#                     return BaseResponse(success=True, error_msg='', result=success)
#             if not blob.exists():
#                 success = parse(request_urls)
#                 upload_file_to_bucket(success, file_path)
#
#                 return BaseResponse(success=True, error_msg='', result=success)
#
#     except :
#         logging.error(traceback.format_exc())
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return BaseResponse(success=False, error_msg='internal error', result=None)
#
#
