"""
Description:
    Database functions for simplifying the storage of crawled data.

Created:
    2024-09-19
"""

from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


async def store_embedding(
    vector: List[float] | List[List[float]],
    metadata: Dict[str, Any] | List[Dict[str, Any]],
    db_client: QdrantClient,
) -> bool:
    """
    Stores data in the qdrant database.

    Parameters
    ----------
    vector : List[float] | List[List[float]]
        The vector or vectors to store. Length must be equal to the
        number of metadata items.

    metadata : Dict[str, Any] | List[Dict[str, Any]]
        The metadata to store with the vector. Length must be equal
        to the number of vectors.

    db_client : QdrantClient
        The Qdrant client to use for storing the data.

    Returns
    -------
    bool
        True if the data was stored successfully, False otherwise.

    Raises
    ------
    ValueError
        If the length of the vector and metadata are not equal.
    """
    # Vector and metadata must be lists for for loop
    if not isinstance(vector, list):
        vector = [vector]

    if not isinstance(metadata, list):
        metadata = [metadata]

    if len(vector) != len(metadata):
        raise ValueError("Vector and metadata must be the same length.")

    # Store embedded vectors and metadata in qdrant
    points = []
    for idx, vector in enumerate(vector):

        points.append(
            PointStruct(
                id=idx,
                vector=vector.tolist(),
                payload={"text": metadata[idx]},
            )
        )
    
    try:
        db_client.upsert(
            collection_name="embeddings",
            points=points
        )
        
    except Exception as e:
        print(e)

        return False

    return True
