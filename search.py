"""
Description:
    This module contains functions for searching the index created by
    the crawler and processor.

Created:
    2024-09-19
"""

import sentence_transformers
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from typing import List, Dict, Any
import numpy as np


def search(
    query: str,
    model: sentence_transformers.SentenceTransformer,
    db_client: QdrantClient,
) -> List[Dict[str, Any]]:
    """
    Searches the qdrant database for the query and returns the
    results.

    Parameters
    ----------
    query : str
        The query to search for.

    model : sentence_transformers.SentenceTransformer
        The sentence_transformers model to use for searching.

    db_client : QdrantClient
        The Qdrant client to use for searching.

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries containing the results of the search.
    """
    vec = model.encode(query, convert_to_numpy=True)
    hits = db_client.search(
        collection_name="search",
        query_vector=vec,
        limit=5,  # Return 5 closest points
    )


async def fetch_matches(
    vector_client: QdrantClient,
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
