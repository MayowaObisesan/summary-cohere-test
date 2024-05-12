import asyncio
import json
import logging
from functools import lru_cache

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from sse_starlette import EventSourceResponse
from fastapi.responses import JSONResponse

import settings
from search_processor import SummarySearchProcessorStream
from settings import summary_allowed_origins, SEARCH_HEADERS
from dummy_search_result import dummy_search_result, dummy_search_result2

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=summary_allowed_origins,
    # allow_origins=["https://createsummary.com", "https://www.createsummary.com", "https://api.createsummary.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("headers")


@app.get('/')
async def root():
    response = {
        'summary': 'hello... 😘👋😉😁🙂😎',
    }
    return response


@lru_cache
@app.get('/summary/single')
async def summary_single(request: Request, search_input: str = None):
    data = await request.json()
    result = await SummarySearchProcessorStream(search_input).fetch_page_summaries(
        data.index, data,
        SEARCH_HEADERS
    )
    return result


@app.get("/search")
async def search(query: str, next_page: bool = False, start_index: int = None):
    if next_page:
        result = SummarySearchProcessorStream(query).google_searcher(
            num=settings.NUMBER_SEARCH_RESULT, start=start_index
        )
    else:
        result = SummarySearchProcessorStream(query).google_searcher(num=settings.NUMBER_SEARCH_RESULT)

    return JSONResponse(result)


@app.get("/search_summary")
async def search_summary(query: str, index: int, url: str):
    result = await SummarySearchProcessorStream(query).fetch_page_summaries_using_url(index, url, SEARCH_HEADERS)
    print("SEARCH SUMMARY RES: ", result)

    return JSONResponse(result)


@app.get("/news")
async def news(
        query: str,
        sources: str,
        language: str = None,
        country: str = None,
        category: str = None,
        next_page: bool = False,
        start_index: int = None
):
    result = SummarySearchProcessorStream(query).news_api()
    logging.info(result)
    return JSONResponse(result)


@app.get("/news_summary")
async def news_summary(query: str, index: int, url: str = None, content: str = None):
    if url:
        result = await SummarySearchProcessorStream(query).fetch_page_summaries_using_url(index, url, SEARCH_HEADERS)
    else:
        result = await SummarySearchProcessorStream(query).fetch_content_summaries(index, content)
    print("NEWS SUMMARY RES: ", result)

    return JSONResponse(result)


@lru_cache
@app.get('/summary')
async def summary(
        request: Request, url_input: str = None, text_input: str = None, search_input: str = None,
        news_input: str = None, news_country: str = "ng",
        file_input: str = None, ai_input: str = None, next_page: bool = False, page_num: int = None,
        start_index: int = None,
        force_summary: bool = None, search_type=None, *, background_tasks: BackgroundTasks
):
    # , internet_available=Depends(is_internet_available)
    # Initialize summary's response
    response_headers: dict = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET,OPTIONS,PATCH,DELETE,POST,PUT",
        "Access-Control-Allow-Headers": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, "
                                        "Content-MD5, Content-Type, Date, X-Api-Version"
    }
    response: dict = dict()
    # if next_page:
    #     search_results = SummarySearchProcessorStream(search_input).google_searcher(
    #         num=settings.NUMBER_SEARCH_RESULT, start=start_index
    #     )
    # else:
    #     search_results = SummarySearchProcessorStream(search_input).google_searcher(
    #         num=settings.NUMBER_SEARCH_RESULT
    #     )
    # response.update({
    #     "search_results": search_results
    # })

    print("OUTER: ", search_input)

    async def event_gens_google_search():
        print("headers")
        print(search_input)
        # index: int = 1
        # start_index: int = 1
        # # each_search_result:
        # number_search_result: int = 10

        # async def summary_streamer():
        # search_results = await SummarySearchProcessorStream(search_input).searcher()
        # SummarySearchProcessorStream(search_input).fetch_page_summary(index, each_search_result, headers)

        # search_results = SummarySearchProcessorStream(search_input).google_searcher(
        #     num=number_search_result, start=start_index
        # )
        # print(search_results)

        search_result_counter = 0
        if next_page:
            print("Next page results")
            print(start_index)
            search_results = SummarySearchProcessorStream(search_input).google_searcher(
                num=settings.NUMBER_SEARCH_RESULT, start=start_index
            )
            # search_results = dummy_search_result2
        else:
            print(search_result_counter)
            search_results = SummarySearchProcessorStream(search_input).google_searcher(
                num=settings.NUMBER_SEARCH_RESULT
            )
            # search_results = dummy_search_result
        # print(search_results.length)

        for f in asyncio.as_completed([
            SummarySearchProcessorStream(search_input).fetch_page_summaries(index, each_search_result, SEARCH_HEADERS)
            for index, each_search_result in enumerate(search_results.get("items"))
        ]):
            result = await f
            # do something with result
            logging.info(result.get('title'))
            # print(result)

            # Increment the search_result_counter for the streaming flag
            search_result_counter += 1
            print(len(search_results.get("items")))
            print(search_result_counter)

            yield json.dumps({
                "event": "new_summary",
                "id": "message_id",
                # "retry": RETRY_TIMEOUT,
                "searchInformation": search_results.get("searchInformation"),
                "queries": search_results.get("queries"),
                "data": result,
                "streaming": True if search_result_counter < len(search_results.get("items")) else False,
                # "streaming": True if len(search_results) < 10 else False,
                "streamed_count": search_result_counter,
                "search_result": search_results.get("items")
            })
            # local_history_list.append(result.get('index'))
            # res = await SummarySearchProcessorStream(search_input).fetch_page(index, each_search_result,
            # headers)
            # self.summarized_search_results.append(res)
            # print(res)
        await request.close()
        logging.info("DONE Generating summaries")
        # logging.info(time.time() - start)

    async def event_gens_news_search():
        search_result_counter = 0
        if next_page:
            print("Next page results")
            print(start_index)
            # news_results = SummarySearchProcessorStream(search_input).news_api(
            #     num=settings.NUMBER_SEARCH_RESULT, start=start_index
            # )
        else:
            news_results = SummarySearchProcessorStream(news_input).news_api()

        for f in asyncio.as_completed([
            SummarySearchProcessorStream(search_input).fetch_content_summaries(index, each_search_result)
            for index, each_search_result in enumerate(news_results.get("articles"))
        ]):
            result = await f
            # do something with result
            logging.info(result.get('title'))

            # Increment the search_result_counter for the streaming flag
            # search_result_counter += 1
            # print(len(news_results.get("items")))
            # print(search_result_counter)

            yield json.dumps({
                "event": "news_summary",
                "id": "message_id",
                # "retry": RETRY_TIMEOUT,
                # "searchInformation": news_results.get("searchInformation"),
                # "queries": news_results.get("queries"),
                "data": result,
                "streaming": True if search_result_counter < len(news_results.get("articles")) else False,
                "streamed_count": search_result_counter,
                "news_result": news_results
            })
        await request.close()
        logging.info("DONE Generating summaries")
        # logging.info(time.time() - start)

    if search_input:
        response_headers.update({"content-type": "text/event-stream"})
        logging.info("BEFORE EVENT SOURCE: " + search_input)
        return EventSourceResponse(
            event_gens_google_search(),
            headers=response_headers
        )

    if news_input:
        response_headers.update({"content-type": "text/event-stream"})
        logging.info("BEFORE EVENT SOURCE: " + search_input)
        return EventSourceResponse(
            event_gens_news_search(),
            headers=response_headers
        )

    print("headers")

    return JSONResponse(response, headers=response_headers)

# async def main():
#     print(await event_gens_google_search())
