"""
Description:
    This module contains functions for searching the index created by
    the crawler and processor.

Created:
    2024-09-19
"""

import sentence_transformers
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import ScoredPoint
from typing import List, Dict, Any
import numpy as np
import asyncpg
from app.models.data_types import Result


async def get_top_matches(
    query: str,
    model: sentence_transformers.SentenceTransformer,
    vector_client: AsyncQdrantClient,
    postgres_client: asyncpg.Connection,
    limit: int = 50,
    match_limit: int = 30,
) -> List[Dict[str, Any]]:
    """
    Search the qdrant database for the query and returns the
    """
    # Embed the query
    search_vector = model.encode(query, convert_to_numpy=True)

    # Get the matches
    matches = await fetch_matches(vector_client, search_vector, limit=limit)

    # Get the best urls by summing scores
    urls = {}
    for match in matches:
        url = match.payload["text"]["url"]
        if url in urls:
            urls[url] += match.score
        else:
            urls[url] = match.score

    # Order the urls by summed score
    top_urls = sorted(urls.items(), key=lambda x: x[1], reverse=True)

    # Reduce the returned urls to the match limit
    top_urls = top_urls[:match_limit]

    # Get the url strings for searching
    top_url_strings = [url for url, _ in top_urls]

    # Get the extra metadata
    url_meta = await postgres_client.fetch(
        "SELECT * FROM resources WHERE url = Any($1::text[])", top_url_strings
    )

    # Add the metadata to the results and return
    top_urls = [
        Result(
            title="",
            siteName="",
            url=url[0],
            snippet="",
            score=url[1],
            faviconLocation="",
            published="",
        )
        for url in top_urls
    ]

    return top_urls


async def fetch_matches(
    vector_client: AsyncQdrantClient,
    search_vector: np.ndarray,
    limit: int = 50,
) -> List[ScoredPoint]:
    """
    Fetch the closest N matches from the qdrant vector database.

    Parameters
    ----------
    vector_client : QdrantClient
        The Qdrant client to use for searching.

    search_vector : np.ndarray
        The vector to search for.

    limit : int, optional
        The maximum number of results to return. Defaults to 50.

    Returns
    -------
    List[ScoredPoint]
        A list of dictionaries containing the results of the search.
    """

    hits = await vector_client.search(
        collection_name="embeddings",
        query_vector=search_vector,
        limit=limit,
    )

    return hits
