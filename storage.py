"""
Description:
    Database functions for simplifying the storage of crawled data.

Created:
    2024-09-19
"""

from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import psycopg2


@dataclass
class Resource:
    url: str
    firstVisited: datetime
    lastVisited: datetime
    allVisits: int
    externalLinks: List[str]


async def store_embedding(
    vector: np.ndarray | List[np.ndarray],
    metadata: Dict[str, Any] | List[Dict[str, Any]],
    vector_client: QdrantClient,
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

    vector_client : QdrantClient
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

        # Create a qdrant point struct
        points.append(
            PointStruct(
                id=idx,
                vector=vector.tolist(),
                payload={"text": metadata[idx]},
            )
        )
    
    # Store points in qdrant
    try:
        vector_client.upsert(
            collection_name="embeddings",
            points=points
        )

    except Exception as e:
        print(e)

        return False

    return True


async def log_resource(
    resource: Resource,
    db_client: psycopg2.extensions.connection,
) -> bool:
    """
    Logs information about a resource to the postgres database.

    Parameters
    ----------
    resource : Resource
        The resource to log.

    db_client : psycopg2.extensions.connection
        The PostgreSQL client to use for logging.

    Returns
    -------
    bool
        True if the resource was logged successfully, False otherwise.
    """
    # Create a tuple of the resource's attributes
    attributes = (
        resource.url,
        resource.firstVisited,
        resource.lastVisited,
        resource.allVisits,
        resource.externalLinks,
    )

    # Log the resource to the database
    try:
        cursor = db_client.cursor()

        await cursor.execute(
            "INSERT INTO resources (url, firstVisited, lastVisited, allVisits, externalLinks) VALUES (%s, %s, %s, %s, %s)",
            attributes,
        )

        return True
    except Exception as e:
        print(e)

        return False