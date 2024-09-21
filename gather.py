"""
Description:
    Sets up the queues for the crawler and processor and starts the
    index building/ updating process.

Created:
    2024-09-19
"""

import crawler
from qdrant_client import QdrantClient
import sentence_transformers
import psycopg2
import asyncio
from crawler import AsyncList, pattern_filter, crawler
from process import process_html_to_vectors


async def gather(
    vector_client: QdrantClient,
    db_client: psycopg2.extensions.connection,
    model: sentence_transformers.SentenceTransformer,
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
    """

    # Create a queue for the crawler
    url_queue = asyncio.Queue()

    # Create a queue for the processor
    response_queue = asyncio.Queue()

    # Create an event to pause the crawler
    pause_crawling = asyncio.Event()

    # Create an event to end the crawler
    stop_crawling = asyncio.Event()

    # Create a list to store seen urls
    seen_urls = AsyncList()

    # Create a crawler coroutine
    asyncio.create_task(process_html_to_vectors(response_queue, model, vector_client))
    await crawler(
        url_queue,
        url_filter={
            "filter_func": pattern_filter,
            "kwargs": {"regex_patterns": ["https://"]},
        },
        client=client,
        response_queue=response_queue,
        pause=pause_crawling,
        end=stop_crawling,
        seen_urls=seen_urls,
        max_iter=1,
    )
