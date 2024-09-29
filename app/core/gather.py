"""
Description:
    Sets up the queues for the crawler and processor and starts the
    index building/ updating process.

Created:
    2024-09-19
"""

from qdrant_client import AsyncQdrantClient
import sentence_transformers
import asyncpg
import asyncio
from crawl import pattern_filter, crawler
from app.models.app_types import AsyncList
from process import process
import datetime
import httpx
from urllib.parse import urlparse
from typing import List


async def gather(
    vector_client: AsyncQdrantClient,
    db_client: asyncpg.Connection,
    model: sentence_transformers.SentenceTransformer,
    revisit_delta: datetime.timedelta = datetime.timedelta(days=1),
    max_iter: int = -1,
    regex_patterns: List[str] | None = None,
):
    """
    Sets up the queues for the crawler and processor and starts the
    index building/ updating process. Uses a db_client and model that
    are passed in.

    Parameters
    ----------
    vector_client : QdrantClient
        The Qdrant client to use for storing vectors.

    db_client : asyncpg.Connection
        The PostgreSQL client to use for storing data.

    model : sentence_transformers.SentenceTransformer
        The sentence_transformers model to use for storing vectors.

    revisit_delta : datetime.timedelta, optional
        The delta to use for revisiting a resource. Defaults to 1 day.
        This is based on the lastVisited attribute of the resources
        taken from the postgres database.

    max_iter : int, optional
        The maximum number of iterations to run the crawler and
        processor for. Defaults to -1, which means run indefinitely.
        This is for testing purposes.

    regex_patterns : List[str] | None, optional
        A list of regex patterns to filter urls by.
    """

    # Create a queue for the crawler
    url_queue = asyncio.Queue()

    # Create a queue for the processor
    response_queue = asyncio.Queue()

    # Event to pause crawler and processor
    pause = asyncio.Event()

    # Event to end crawler and processor
    end = asyncio.Event()

    # Create a list to store seen urls
    seen_urls = AsyncList()

    # Create an httpx client
    client = httpx.AsyncClient(follow_redirects=True)

    # Get all the urls from the postgres database
    all_urls = await db_client.fetch("SELECT url, lastVisited FROM resources")

    # Filter out the urls to be revisited
    current_time = datetime.datetime.now()
    retry_urls = [url[0] for url in all_urls if current_time - url[1] > revisit_delta]

    print("retry urls:", retry_urls)

    # Add the retry urls to the url queue
    for url in retry_urls:
        await url_queue.put(url)

    print("url queue:", url_queue.qsize())

    # Add the remaining seen urls to the seen urls list
    remaining_urls = [url[0] for url in all_urls if url not in retry_urls]
    for url in remaining_urls:
        await seen_urls.append(url)

    print("seen urls:", seen_urls)

    # Create a process coroutine
    task = asyncio.create_task(
        process(
            response_queue,
            model,
            vector_client,
            db_client,
            pause,
            end,
            max_iter=max_iter,
        )
    )

    print("task:", task)

    # Filter patterns for urls
    url_filter = {
        "filter_func": pattern_filter,
        "kwargs": {
            "regex_patterns": (
                retry_urls if regex_patterns is None else regex_patterns
            ),
        },
    }

    # Create a crawler coroutine
    await crawler(
        url_queue,
        url_filter=url_filter,
        client=client,
        response_queue=response_queue,
        pause=pause,
        end=end,
        seen_urls=seen_urls,
        max_iter=max_iter,
    )

    # Wait for the process coroutine to finish
    end.set()
    await task
