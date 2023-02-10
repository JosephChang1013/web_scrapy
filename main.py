from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dependency.open_api_dependency import get_current_username

from routers.Chinatime_news_router import chinatime_router
from routers.Ettoday_router import ettoday_router
from routers.Now_new_router import now_router
from routers.Tvbs_news_router import tvbsnews_router
# from routers.loader import scrapy_router
from routers.dcard_router import dcard_router
from routers.ptt_router import ptt_router
from routers.schedule import schedule_router
from routers.tokenization_router import tokenization_router
from routers.udn_news_router import udn_router

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.secret_key = b'yvEyzxkS3ury7CTfd2BZvIJa58PCgIFpJhsQJvRMi4ObzVBxQFjA4WWhfVj3rwRd083Yx4YsR9MPXPpSafKhVfTDVDZyxDumB0WZ1oepqZNyFo2fFnLwz8gmqHGQtdXG'

# routers
prefix = '/web_scraper/api'
# app.include_router(scrapy_router, prefix=prefix, tags=['scrapy'])
app.include_router(schedule_router, prefix=prefix, tags=['schedule'])
app.include_router(ettoday_router, prefix=prefix, tags=['schedule'])
app.include_router(udn_router, prefix=prefix, tags=['schedule'])
app.include_router(now_router, prefix=prefix, tags=['schedule'])
app.include_router(chinatime_router, prefix=prefix, tags=['schedule'])
app.include_router(tvbsnews_router, prefix=prefix, tags=['schedule'])
app.include_router(dcard_router, prefix=prefix, tags=['schedule'])
app.include_router(ptt_router, prefix=prefix, tags=['schedule'])
app.include_router(tokenization_router, prefix=prefix, tags=['tokenization'])


# open api
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title="web_scraper", version="1.0.0", routes=app.routes)


# startup
@app.on_event("startup")
async def startup_event():
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
