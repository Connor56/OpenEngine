"""
Description:
    Sets up the queues for the crawler and processor and starts the
    index building/ updating process.

Created:
    2024-09-19
"""

from qdrant_client import QdrantClient
import sentence_transformers
import psycopg2
import asyncio
from crawl import AsyncList, pattern_filter, crawler
from process import process
import datetime
import httpx


async def gather(
    vector_client: QdrantClient,
    db_client: psycopg2.extensions.connection,
    model: sentence_transformers.SentenceTransformer,
    revisit_delta: datetime.timedelta = datetime.timedelta(days=1),
    max_iter: int = -1,
):
    """
    Sets up the queues for the crawler and processor and starts the
    index building/ updating process. Uses a db_client and model that
    are passed in.

    Parameters
    ----------
    vector_client : QdrantClient
        The Qdrant client to use for storing vectors.

    db_client : psycopg2.extensions.connection
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
    client = httpx.AsyncClient()

    # Get all the urls from the postgres database
    cursor = db_client.cursor()
    cursor.execute("SELECT url, lastVisited FROM resources")
    all_urls = cursor.fetchall()

    # Filter out the urls to be revisited
    current_time = datetime.datetime.now()
    retry_urls = [url[0] for url in all_urls if current_time - url[1] > revisit_delta]

    # Add the retry urls to the url queue
    for url in retry_urls:
        await url_queue.put(url)

    # Add the remaining seen urls to the seen urls list
    remaining_urls = [url[0] for url in all_urls if url not in retry_urls]
    for url in remaining_urls:
        await seen_urls.append(url)

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

    # Create a crawler coroutine
    await crawler(
        url_queue,
        url_filter={
            "filter_func": pattern_filter,
            "kwargs": {"regex_patterns": ["https://"]},
        },
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
