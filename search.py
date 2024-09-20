"""
Description:
    This module contains functions for searching the index created by
    the crawler and processor.

Created:
    2024-09-19
"""

import sentence_transformers
from qdrant_client import QdrantClient
from typing import List, Dict, Any


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
