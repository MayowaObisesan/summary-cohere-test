import asyncio
import json
import logging
import re
import time
import uuid
from typing import Union

import aiohttp
import requests
from bs4 import BeautifulSoup, NavigableString, TemplateString, CData
from sse_starlette import EventSourceResponse
from yarl import URL

import settings
# from history_processor import SummaryHistoryProcessor
from utils import how_to_clean_html_definition

# logging.basicConfig(format=f'%(asctime)s - %(levelname)s:::%(message)s', level=logging.INFO)
logging.basicConfig(format=f'%(levelname)s:::%(message)s', level=logging.INFO)

stream_container = list()
NEW_SUMMARY = False


def is_new_summary():
    NEW_SUMMARY = True


def reset_new_summary():
    NEW_SUMMARY = False


class SummarySearchProcessor:
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

    def __init__(self, search_string: str):
        self.headers = {
            "Authorization": f"Bearer {settings.API_TOKEN}"
        }
        self.search_string = search_string

    def query(self):
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        url = ask_search.get_search_url(self.search_string, latest=True)
        response = requests.request("GET", url, headers=headers)
        html = response.text
        results, next_page_url = ask_search.extract_search_results(html, url)
        return [{'results': results, 'next_page_url': next_page_url}]

    def search_summary(self):
        results = self.query()[0].get("results")
        print(results)
        for index, _ in enumerate(results):
            payload = {
                "inputs": html_parsed_content(_.get("url")),
                "parameters": {
                    "do_sample": SummaryModelAPIParameters.DO_SAMPLE,
                    "min_length": SummaryModelAPIParameters.MIN_LENGTH,
                    "max_length": SummaryModelAPIParameters.MAX_LENGTH,
                    "top_k": SummaryModelAPIParameters.TOP_K,
                    "top_p": SummaryModelAPIParameters.TOP_P,
                    "temperature": SummaryModelAPIParameters.TEMPERATURE,
                },
                "options": {}
            }
            response = requests.request("POST", BASE_API_URL, headers=self.headers, data=json.dumps(payload))
            summarized_response = json.loads(response.content.decode("utf-8"))
            # print(summarized_response)
            print(index)
            if type(summarized_response) is dict:
                if summarized_response.get('error'):
                    return summarized_response
            if len(summarized_response[0].get("summary_text").split(
                    " ")) <= SummaryModelAPIParameters.MIN_LENGTH_THRESHOLD:
                results[index].update({"summary": results[index].get('preview_text')})
            else:
                results[index].update({"summary": summarized_response[0].get('summary_text')})
        # print(results)
        print("PRINTING RESULTS")
        return results


class SummarySearchProcessorStream:
    API_TOKEN = "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"
    MODEL_HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}
    MODEL_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

    def __init__(self, search_input: str):
        # Setup API call
        self.headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
        }
        self.search_input = search_input
        self.payloads = list()
        self.summarized_search_results = list()

    def google_searcher(self, **kwargs):
        """
        Perform a Google search using Custom Search API
        :Date: March 30, 2023.
        """
        from googleapiclient.discovery import build
        # Build request
        # Create a client object for the Google Custom Search API, version 1
        service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
        # Execute request
        query_result = service.cse().list(q=self.search_input, cx=settings.GOOGLE_CSE_ID, **kwargs).execute()
        print("GOOGLE searcher")
        print(query_result.get("queries"))
        return query_result

    async def searcher(self, current_page: int = 1, pages_to_search: int = 1):
        """
        This method performs the search using the async search engine library
        :param current_page: The page to begin the search from
        :param pages_to_search: Number of page(s) to search
        :return: coroutine of result
        """
        from search_engines import (
            Google, Bing, Ask, Yahoo, Torch, Aol, Dogpile, Duckduckgo, Mojeek, Qwant, Startpage,
            multiple_search_engines,
            config
        )
        s_time = time.time()
        logging.info(f"Pages to search: {pages_to_search}")
        PAGES_TO_SEARCH = config.SEARCH_ENGINE_RESULTS_PAGES = pages_to_search
        # engine = Google()
        # engine = Bing()
        # engine = Torch()
        # engine = Yahoo()
        # engine = Brave()
        # engine = Ask()
        engine = Duckduckgo()
        # engine = multiple_search_engines.MultipleSearchEngines(["google", "yahoo"])
        engine._current_page = current_page
        logging.info(f"Searching from page: {current_page} to page {pages_to_search}")
        query_results = await engine.search(self.search_input, pages=PAGES_TO_SEARCH)
        links = query_results.links()
        titles = query_results.titles()
        hosts = query_results.hosts()
        result = query_results.results()
        logging.info("Search complete")
        logging.info("Took %s " % (time.time() - s_time))
        logging.info("%d results" % len(query_results))
        return result

    def search_eng(self, search_query: str):
        url = ask_search.get_search_url(search_query, latest=True)
        response = requests.request("GET", url, headers=self.headers)
        html = response.text
        results, next_page_url = ask_search.extract_search_results(html, url)
        # return [{'results': results, 'next_page_url': next_page_url}]
        return results

    async def summarize(self, input_payload: Union[str, dict], session):
        data = json.dumps(input_payload)
        start_time = time.time()
        async with session.post(self.MODEL_API_URL, headers=self.MODEL_HEADERS, json=data) as response:
            json_response = await response.json()
            # print(json_response)
            end_time = time.time()
            # logging.info("gotten response %s" % str(end_time - start_time))
        return json_response
        # res = await self.gather_with_concurrency(conc_req, *[self.post_async(each_payload, session, self.headers) for each_payload in self.payloads])
        # response = requests.request("POST", MODEL_API_URL, headers=headers, data=data)
        # return json.loads(response.content.decode("utf-8"))

    @staticmethod
    async def cohere_summarize(text_to_summarize: str) -> str:
        import cohere
        co = cohere.Client(settings.COHERE_API_KEY)  # This is your trial API key
        response = co.summarize(
            text=text_to_summarize,
            length='auto',
            format='bullets',
            model='command',
            additional_command='',
            temperature=0.8,
        )
        return response.summary

    # async def ping_summary(self, json_response):
    #     STREAM_DELAY = 1    # second
    #     RETRY_TIMEOUT = 15000   # millisecond
    #     # json_response = self.summarize(input_payload, session)
    #     # yield json_response
    #     # return json_response
    #
    #     async def event_generator():
    #         while True:
    #             # If client closes the connection, stop sending events
    #             # if await request.is_disconnected():
    #             #     break
    #
    #             # Check for new messages and return them to the client if any
    #             if json_response:
    #                 logging.info(json_response)
    #                 # yield {
    #                 #     "event": "new_message",
    #                 #     "id": "message_id",
    #                 #     "retry": RETRY_TIMEOUT,
    #                 #     "data": "message_content"
    #                 # }
    #                 yield json_response
    #             # await asyncio.sleep(STREAM_DELAY)
    #     return EventSourceResponse(event_generator())

    # Create Async function to run requests concurrently
    # Gather asynchronous Python requests to run concurrently
    # SEND AND GATHER ASYNCHRONOUS REQUESTS IN PYTHON
    @staticmethod
    async def gather_with_concurrency(n, *tasks):
        semaphore = asyncio.Semaphore(n)

        async def sem_task(task):
            try:
                async with semaphore:
                    return await task
            except Exception:
                pass

        return await asyncio.gather(*(sem_task(task) for task in tasks), return_exceptions=True)

    @staticmethod
    async def process_concurrently(n, *tasks):
        for f in asyncio.as_completed([task for task in tasks]):
            result = await f
            # do something with result
            logging.info(result.get('title'))
        logging.info(f"Completed {len(tasks)} tasks")
        # SummaryHistoryProcessor().create_history(str(result.get("index")), result)

    # async def process_all_concurrently(self, *tasks):
    #     tasks_list = []
    #
    #     async for obj in tasks:
    #         # Python 3.7+ only. For older versions, use ensure_future
    #         task = asyncio.create_task(self.fetch_page)

    # Create Python Asynchronous API call function
    async def fetch_page(self, index, obj: dict, headers):
        url = obj.get("link")
        # print("Got the url link")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL(url), headers=headers) as response:
                    # print(response)
                    # print(response.content_type)
                    # print(response.get_encoding())
                    # Check the response's content_type, as it can break the execution loop
                    # Added this check - March 5, 2023. 18:41
                    if response.content_type == "text/html":
                        text = await response.text(encoding='utf-8')
                        # Add BS parsing here, and return it.
                        soup = BeautifulSoup(str(text), 'lxml')
                        page_icon = soup.find("link", attrs={'rel': 'icon'})
                        page_icon = page_icon.get('href') if page_icon else ""
                        # logging.info(page_icon)
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '128x128'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '96x96'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '256x256'})
                        [_.decompose() for _ in soup.find_all(how_to_clean_html_definition)]
                        page_text = soup.get_text(separator="\n", strip=True,
                                                  types=(NavigableString, CData, TemplateString))

                        # Remove some unnecessary
                        page_text_list: list = list()
                        for _ in page_text.split("."):
                            # _ = _.replace("\n", " ")
                            _ = re.sub(r'\s{1,}', ' ', _)
                            if len(_.split(" ")) <= 4:
                                continue
                            page_text_list.append(_)
                        cleaned_page_text = "".join(page_text_list)
                        # print(f"{url} - {page_text}")
                        # print(page_text, end="\n\n")
                        # return json.loads(text)
                        # return text
                        payload = {
                            'inputs': cleaned_page_text,
                            'parameters': {
                                'do_sample': False,
                                # 'min_length': 248,
                                'min_length': 428,
                                # 'max_length': 824,
                                'max_length': 1024,
                                'top_k': len(cleaned_page_text.split(" ")) / 2,
                                # 'top_p': 0.92,
                                'top_p': 0.2,
                                'temperature': 90.0
                            },
                            'options': {
                                'use_cache': True
                            }
                        }
                        # self.payloads.append(payload)
                        if len(page_text.split(" ")) < 48:
                            obj.update(
                                {'summary_text': page_text or obj.get('text'), 'icon': page_icon, 'index': index})
                        else:
                            summary = await self.summarize(payload, session)
                            # print(summary[0])
                            obj.update(summary[0] if type(summary) == list else summary)
                            obj.update({'icon': page_icon, 'index': index})
                        # is_new_summary()
                        # print("Received new summary, updating local DB")
                        # SummaryHistoryProcessor().create_history(str(index), obj)
                    elif response.content_type.startswith("application/"):
                        logging.info(f"DETECTED APPLICATION CONTENT TYPE: {response.content_type}")
                        if response.content_type == "application/pdf":
                            # process the pdf file and return the summary of the pdf file.
                            ...
        except asyncio.TimeoutError:
            logging.warning(f"{url} timed out")
            # raise asyncio.TimeoutError({"error": f"{url} - Request timeout"})
        except aiohttp.ServerTimeoutError as err:
            logging.error("Server timed out")
            # Resend the current request
            # raise aiohttp.ServerTimeoutError({"error": "Client Timeout. Kindly Try again"})
        except aiohttp.ClientConnectorCertificateError:
            logging.error("Certificate error occurred")
            # raise {"error": "Connection Error"}
            pass
        except aiohttp.ClientConnectorError:
            logging.error("Client connector error occurred")
            # raise {"error": "Connection Error occurred"}
            pass
        except aiohttp.ServerConnectionError:
            logging.error("Server connection error")
            # raise aiohttp.ServerConnectionError({"error": "Server Disconnected. Kindly Try again"})
            pass
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            pass
        # logging.info(f"Added {len(self.payloads)} payloads")
        return obj

    async def fetch_page_summary(self, index, obj: dict, headers):
        url = obj.get("link")
        # print("Got the url link")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL(url), headers=headers) as response:
                    # print(response)
                    # print(response.content_type)
                    # print(response.get_encoding())
                    # Check the response's content_type, as it can break the execution loop
                    # Added this check - March 5, 2023. 18:41
                    if response.content_type == "text/html":
                        text = await response.text(encoding='utf-8')
                        # Add BS parsing here, and return it.
                        soup = BeautifulSoup(str(text), 'lxml')
                        page_icon = soup.find("link", attrs={'rel': 'icon'})
                        page_icon = page_icon.get('href') if page_icon else ""

                        # logging.info(page_icon)
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '128x128'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '96x96'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '256x256'})
                        [_.decompose() for _ in soup.find_all(how_to_clean_html_definition)]
                        page_text = soup.get_text(separator="\n", strip=True,
                                                  types=(NavigableString, CData, TemplateString))

                        # Remove some unnecessary
                        page_text_list: list = list()
                        for _ in page_text.split("."):
                            # _ = _.replace("\n", " ")
                            _ = re.sub(r'\s{1,}', ' ', _)
                            if len(_.split(" ")) <= 4:
                                continue
                            page_text_list.append(_)
                        cleaned_page_text = "".join(page_text_list)
                        # print(f"{url} - {page_text}")
                        # print(page_text, end="\n\n")
                        # return json.loads(text)
                        # return text
                        payload = {
                            'inputs': cleaned_page_text,
                            'parameters': {
                                'do_sample': False,
                                # 'min_length': 248,
                                'min_length': 428,
                                # 'max_length': 824,
                                'max_length': 1024,
                                'top_k': len(cleaned_page_text.split(" ")) / 2,
                                # 'top_p': 0.92,
                                'top_p': 0.2,
                                'temperature': 90.0
                            },
                            'options': {
                                'use_cache': True
                            }
                        }
                        # self.payloads.append(payload)
                        if len(page_text.split(" ")) < 48:
                            obj.update(
                                {'summary_text': page_text or obj.get('text'), 'index': index, 'icon': page_icon})
                        else:
                            summary = await self.summarize(payload, session)
                            # print(summary[0])
                            obj.update(summary[0] if type(summary) == list else summary)
                            obj.update({'index': index, 'icon': page_icon})
                        # is_new_summary()
                        # print("Received new summary, updating local DB")
                        # SummaryHistoryProcessor().create_history(str(index), obj)
                    elif response.content_type.startswith("application/"):
                        logging.info(f"DETECTED APPLICATION CONTENT TYPE: {response.content_type}")
                        if response.content_type == "application/pdf":
                            # process the pdf file and return the summary of the pdf file.
                            ...
        except asyncio.TimeoutError:
            logging.warning(f"{url} timed out")
            # raise asyncio.TimeoutError({"error": f"{url} - Request timeout"})
        except aiohttp.ServerTimeoutError as err:
            logging.error("Server timed out")
            # Resend the current request
            # raise aiohttp.ServerTimeoutError({"error": "Client Timeout. Kindly Try again"})
        except aiohttp.ClientConnectorCertificateError:
            logging.error("Certificate error occurred")
            # raise {"error": "Connection Error"}
            pass
        except aiohttp.ClientConnectorError:
            logging.error("Client connector error occurred")
            # raise {"error": "Connection Error occurred"}
            pass
        except aiohttp.ServerConnectionError:
            logging.error("Server connection error")
            # raise aiohttp.ServerConnectionError({"error": "Server Disconnected. Kindly Try again"})
            pass
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            pass
        # logging.info(f"Added {len(self.payloads)} payloads")
        return obj

    async def fetch_page_summaries(self, index, obj: dict, headers):
        url = obj.get("link")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL(url), headers=headers) as response:
                    # print(response)
                    # print(response.content_type)
                    # print(response.get_encoding())
                    # Check the response's content_type, as it can break the execution loop
                    # Added this check - March 5, 2023. 18:41
                    # print(dir(response))
                    print(response.status)
                    if response.content_type == "text/html":
                        text = await response.text(encoding='utf-8')
                        # Add BS parsing here, and return it.
                        soup = BeautifulSoup(str(text), 'lxml')
                        page_icon = soup.find("link", attrs={'rel': 'icon'})
                        page_icon = page_icon.get('href') if page_icon else ""

                        # logging.info(page_icon)
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '128x128'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '96x96'})
                        # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '256x256'})
                        [_.decompose() for _ in soup.find_all(how_to_clean_html_definition)]
                        page_text = soup.get_text(separator="\n", strip=True,
                                                  types=(NavigableString, CData, TemplateString))

                        # Remove some unnecessary
                        page_text_list: list = list()
                        for _ in page_text.split("."):
                            # _ = _.replace("\n", " ")
                            _ = re.sub(r'\s{1,}', ' ', _)
                            if len(_.split(" ")) <= 4:
                                continue
                            page_text_list.append(_)
                        cleaned_page_text = "".join(page_text_list)
                        # print(f"{url} - {page_text}")
                        # print(page_text, end="\n\n")
                        # return json.loads(text)
                        # return text
                        # payload = {
                        #     'inputs': cleaned_page_text,
                        #     'parameters': {
                        #         'do_sample': False,
                        #         # 'min_length': 248,
                        #         'min_length': 428,
                        #         # 'max_length': 824,
                        #         'max_length': 1024,
                        #         'top_k': len(cleaned_page_text.split(" ")) / 2,
                        #         # 'top_p': 0.92,
                        #         'top_p': 0.2,
                        #         'temperature': 90.0
                        #     },
                        #     'options': {
                        #         'use_cache': True
                        #     }
                        # }
                        # self.payloads.append(payload)
                        # if len(page_text.split(" ")) < 48:
                        #     obj.update(
                        #         {'summary_text': page_text or obj.get('text'), 'index': index, 'icon': page_icon})
                        # else:
                        #     summary = await self.summarize(payload, session)
                        #     # print(summary[0])
                        #     obj.update(summary[0] if type(summary) == list else summary)
                        #     obj.update({'index': index, 'icon': page_icon})
                        # is_new_summary()
                        # print("Received new summary, updating local DB")
                        # SummaryHistoryProcessor().create_history(str(index), obj)
                        if len(page_text.split(" ")) < 48:
                            obj.update({
                                'summary_text': page_text or obj.get('text'),
                                'index': index,
                                'icon': page_icon
                            })
                        else:
                            summary = await self.cohere_summarize(cleaned_page_text)
                            # logging.info(summary)
                            # obj.update({"summary_text": summary})
                            obj.update({
                                'index': index,
                                'icon': page_icon,
                                'summary_text': summary
                            })
                    elif response.content_type.startswith("application/"):
                        logging.info(f"DETECTED APPLICATION CONTENT TYPE: {response.content_type}")
                        if response.content_type == "application/pdf":
                            # process the pdf file and return the summary of the pdf file.
                            ...
        except asyncio.TimeoutError:
            # Return the content of the website if it timed out.
            logging.warning(f"{url} timed out")
            return obj
            # raise asyncio.TimeoutError({"error": f"{url} - Request timeout"})
        except aiohttp.ServerTimeoutError as err:
            logging.error("Server timed out")
            # Resend the current request
            # raise aiohttp.ServerTimeoutError({"error": "Client Timeout. Kindly Try again"})
        except aiohttp.ClientConnectorCertificateError:
            logging.error("Certificate error occurred")
            # raise {"error": "Connection Error"}
            pass
        except aiohttp.ClientConnectorError:
            logging.error("Client connector error occurred")
            # raise {"error": "Connection Error occurred"}
            pass
        except aiohttp.ServerConnectionError:
            logging.error("Server connection error")
            # raise aiohttp.ServerConnectionError({"error": "Server Disconnected. Kindly Try again"})
            pass
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            pass
            # logging.info(f"Added {len(self.payloads)} payloads")
        return obj


# Call multiple APIs Asynchronously in Python with AIOHTTP
async def main(self):
    start_time = time.time()
    # Create a TCPConnector object
    # conn = aiohttp.TCPConnector(limit=1000, ttl_dns_cache=3000)
    # Setup the HTTP session.
    # session = aiohttp.ClientSession(connector=conn)
    conc_req = 40

    # Perform the search
    # search_results = await self.searcher()
    search_results = self.google_searcher()
    queries = search_results.get("queries")
    search_information = search_results.get("searchInformation")
    search_items = search_results.get("items")
    print(f"queries: {queries}")
    print(f"search_information: {search_information}")
    print(f"search_items: {search_items}")

    # Execute Gathered Requests with aiohttp
    # res = await gather_with_concurrency(conc_req, *[post_async(url, session, headers) for url in urls])
    # res = await self.gather_with_concurrency(conc_req, *[self.fetch_page(each_search_result, self.headers) for each_search_result in search_results])
    # res = await self.process_concurrently(conc_req, *[self.fetch_page(index, each_search_result, self.headers) for index, each_search_result in enumerate(search_results)])
    # res = await self.process_concurrently(conc_req,
    #                                       *[self.fetch_page_summary(index, each_search_result, self.headers) for
    #                                         index, each_search_result in enumerate(search_results.items)])
    res = await self.process_concurrently(
        conc_req,
        *[
            self.fetch_page_summaries(index, each_search_result, self.headers)
            for index, each_search_result in enumerate(search_results.items)
        ]
    )
    logging.info("Done fetching payload... Begin summarization")

    # Fetch each of the search_results
    # for index, each_search_result in enumerate(search_results):
    #     res = await self.fetch_page(index, each_search_result, self.headers)
    #     self.summarized_search_results.append(res)
    # res = [await self.fetch_page(each_search_result, self.headers) for each_search_result in search_results]
    # async def process_all():
    #     tasks = []
    #
    #     async for obj in search_results:
    #         task = asyncio.create_task(self.fetch_page(0, obj, self.headers))
    #         tasks.append(task)
    #     await asyncio.gather(*tasks)
    # await process_all()
    end_time = time.time()
    print("Took: ", str(end_time - start_time))
    # return {"results": res}


async def run(self):
    # Run the main function
    # asyncio.get_event_loop().run_until_complete(self.main())
    print("Done")

    await self.main()
    return self.summarized_search_results
