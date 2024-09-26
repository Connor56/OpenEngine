"""
Description:
    Crawler function and other functions used to assist in
    asynchronous crawling. 

Created:
    2024-09-14
"""

import httpx
import asyncio
from typing import Dict, Any, Callable, Optional
from bs4 import BeautifulSoup
from typing import List
import re
from urllib.parse import urlparse, urlunparse
from utility import get_base_site, clean_urls, handle_relative_url


class AsyncList:
    """
    Simple asyncronous list class that allows for thread safe
    appending and popping.
    """

    def __init__(self):
        self._list = []
        self._lock = asyncio.Lock()

    async def append(self, item):
        async with self._lock:
            self._list.append(item)

    async def get_all(self):
        async with self._lock:
            return list(self._list)

    async def pop(self):
        async with self._lock:
            if self._list:
                return self._list.pop(0)
            return None


def pattern_filter(
    urls: List[str],
    regex_patterns: List[str],
) -> List[str]:
    """
    Searches a list of urls for regular expression patterns and keeps
    only those that match one of the patterns. This is a whitelist
    style pattern matching function.
    """
    regex_patterns = [re.compile(pattern) for pattern in regex_patterns]
    filtered_urls = []
    for url in urls:
        for pattern in regex_patterns:
            match = pattern.search(url)
            if match is not None:
                filtered_urls.append(url)
                break

    print("these are the filtered urls:", filtered_urls)
    return filtered_urls


async def crawler(
    url_queue: asyncio.Queue,
    url_filter: Dict[str, Any],
    client: httpx.AsyncClient,
    response_queue: asyncio.Queue,
    pause: asyncio.Event,
    end: asyncio.Event,
    seen_urls: Optional[AsyncList] = [],
    max_iter: Optional[int] = -1,
) -> None:
    """
    Simple asynchronous crawling function that continuously reads
    urls from the url queue and adds the responses to a response
    queue that can be consumed by a response processor.

    Parameters
    ----------
    url_queue : asyncio.Queue
        The queue that contains the urls to crawl.

    url_filter : Dict[str, Any]
        A dictionary that must contain a "filter_func" key that
        is a callable function and a "kwargs" key that is a dictionary
        of keyword arguments to pass to the filter function.

    client : httpx.AsyncClient
        The httpx client to use for making requests.

    response_queue : asyncio.Queue
        The queue to push responses from the request to.

    pause : asyncio.Event
        The event to pause the crawler's while loop. This lets you
        stop and start the crawler.

    end : asyncio.Event
        Ends the crawler's while loop.

    seen_urls : AsyncList, optional
        The list of urls that have already been crawled. This is
        used to prevent crawling the same url multiple times. It can
        be shared across multiple crawlers.

    max_iter : int, optional
        The maximum number of iterations to run the crawler for.
    """
    num_iter = 0
    while not pause.is_set():
        # Crawler ended?
        if end.is_set():
            break

        # Max crawl iterations reached?
        if max_iter != -1 and num_iter >= max_iter:
            break
        else:
            num_iter += 1

        url = await url_queue.get()
        url_queue.task_done()

        soup = None
        response = await client.get(url)

        # Get soup object on success
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")

            response_queue.put_nowait(soup)

        # Get all links from the soup
        if soup is not None:
            all_links = soup.find_all("a")
            all_links = [link.get("href") for link in all_links]

        # Filter the links
        filter_func = url_filter["filter_func"]
        filter_kwargs = url_filter["kwargs"]

        addable_urls = filter_func(all_links, **filter_kwargs)

        # Retrieve seen urls
        if isinstance(seen_urls, AsyncList):
            all_urls = await seen_urls.get_all()
        else:
            all_urls = seen_urls[:]

        # Add unseen urls to crawl queue
        for url in addable_urls:
            # Check it hasn't already been seen
            if url not in all_urls:
                await url_queue.put(url)
                seen_urls.append(url)


