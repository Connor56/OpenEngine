"""
Description:
    Database functions for simplifying the storage of crawled data.

Created:
    2024-09-19
"""

from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import asyncpg
from uuid import uuid4
from urllib.parse import urlparse
from app.models.data_types import CrawledUrl, PotentialUrl, SeedUrl
from app.core.utility import check_url


@dataclass
class Resource:
    url: str
    firstVisited: datetime
    lastVisited: datetime
    allVisits: int
    externalLinks: List[str]


async def store_embedding(
    vector: np.ndarray | List[np.ndarray] | List[float] | List[List[float]],
    metadata: Dict[str, Any] | List[Dict[str, Any]],
    vector_client: AsyncQdrantClient,
) -> bool:
    """
    Stores data in the qdrant database.

    Parameters
    ----------
    vector : np.ndarray | List[np.ndarray]
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
                id=uuid4().hex,
                vector=(
                    vector.tolist()
                    if isinstance(vector, np.ndarray)
                    else vector
                ),
                payload={"text": metadata[idx]},
            )
        )

    # Store points in qdrant
    try:
        await vector_client.upsert(
            collection_name="embeddings",
            points=points,
            wait=True,
        )

    except Exception as e:
        print(e)

        return False

    return True


async def log_resource(
    resource: Resource,
    db_client: asyncpg.Connection,
) -> bool:
    """
    Logs information about a resource to the postgres database, if it isn't already
    present.

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

        await db_client.execute(
            "INSERT INTO resources (url, firstVisited, lastVisited, allVisits, externalLinks) VALUES ($1, $2, $3, $4, $5)",
            *attributes,
        )

        return True
    except Exception as e:
        print("Failed to load resource with error:", e)

        return False


async def add_potential_url(
    url: str,
    time_seen: datetime,
    db_client: asyncpg.Connection,
) -> bool:
    """
    Adds a new potential url to the database, that isn't crawled
    but could be added to the crawlable set of urls in the future.

    Parameters
    ----------
    url : str
        The url to add.

    time_seen : datetime
        The time the url was seen. Will only be stored if this is
        the first time the url has been seen.

    db_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    bool
        True if the url was added successfully, False otherwise.
    """
    # Check the url is valid
    if not check_url(url):
        print("Invalid url:", url)

        return False

    # Check the url hasn't already been added
    query = "SELECT * FROM potential_urls WHERE url = $1"
    result = await db_client.fetchrow(query, url)

    # If the url has already been added, update the timesSeen
    if result is not None:
        print("Url already added:", url)

        query = (
            "UPDATE potential_urls SET timesSeen = timesSeen + 1 WHERE url = $1"
        )

        await db_client.execute(query, url)

        return True

    # Create a tuple of the resource's attributes
    attributes = (url, time_seen, 1)

    # Log the potential url in the database
    try:

        await db_client.execute(
            "INSERT INTO potential_urls (url, firstSeen, timesSeen) VALUES ($1, $2, $3)",
            *attributes,
        )

        return True

    except Exception as e:
        print("Failed to add url with error:", e)

        return False


async def add_seed_url(
    url: str,
    seeds: List[str],
    db_client: asyncpg.Connection,
) -> bool:
    """
    Adds a new seed url to the database.

    Parameters
    ----------
    url : str
        The url to add.

    db_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    bool
        True if the url was added successfully, False otherwise.
    """
    # Check the url is valid and return false if it isn't
    if not check_url(url):
        print("Invalid url:", url)

        return False

    # Create a tuple of the resource's attributes
    attributes = (url, seeds)

    # Log the resource to the database
    try:

        await db_client.execute(
            "INSERT INTO seed_urls (url, seeds) VALUES ($1, $2)",
            *attributes,
        )

        return True
    except Exception as e:
        print("Failed to add url with error:", e)

        return False


async def delete_seed_url(
    url: str,
    db_client: asyncpg.Connection,
) -> bool:
    """
    Deletes a seed url from the database.

    Parameters
    ----------
    url : str
        The url to delete.

    db_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    bool
        True if the url was deleted successfully, False otherwise.
    """
    # Create a tuple of the resource's attributes
    attributes = (url,)

    # Log the resource to the database
    try:

        await db_client.execute(
            "DELETE FROM seed_urls WHERE url = $1",
            *attributes,
        )

        return True

    except Exception as e:
        print("Failed to delete url with error:", e)

        return False


async def update_seed_url(
    old_url: str,
    new_url: str,
    postgres_client: asyncpg.Connection,
) -> bool:
    """
    Updates a seed url in the database.

    Parameters
    ----------
    old_url : str
        The old url to update.

    new_url : str
        The new url to update to.

    postgres_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    bool
        True if the url was updated successfully, False otherwise.
    """
    # Create a tuple of the resource's attributes
    attributes = (new_url, old_url)

    # Log the resource to the database
    try:

        await postgres_client.execute(
            "UPDATE seed_urls SET url = $1 WHERE url = $2",
            *attributes,
        )

        return True

    except Exception as e:
        print("Failed to update url with error:", e)

        return False


async def add_seed_to_url(
    seed: str,
    url: str,
    postgres_client: asyncpg.Connection,
):
    """
    Adds a seed to an url in the database.
    """
    # Get the current array of seeds for the url
    current_seeds = await postgres_client.fetchrow(
        "SELECT seeds FROM seed_urls WHERE url = $1", url
    )

    # Get the current seeds list
    current_seeds = current_seeds[0]

    # Replace a None value with an empty list
    if current_seeds is None:
        current_seeds = []

    # Check if the seed is already in the array
    if seed in current_seeds:
        print("Seed already in array:", seed)
        return False

    # Else add the seed to the array
    current_seeds.append(seed)

    try:
        # Update the array in the database
        await postgres_client.execute(
            "UPDATE seed_urls SET seeds = $1 WHERE url = $2", current_seeds, url
        )

        return True

    # If this fails for some reason, print the exception
    except Exception as e:
        print("Failed to update url with error:", e)

        return False


async def delete_seed_from_url(
    seed: str,
    url: str,
    postgres_client: asyncpg.Connection,
):
    """
    Deletes a seed from an url in the database.
    """
    # Get the current array of seeds for the url
    current_seeds = await postgres_client.fetchrow(
        "SELECT seeds FROM seed_urls WHERE url = $1", url
    )

    current_seeds = current_seeds[0]

    # Handle the case where the seed array is None
    if current_seeds is None:
        return (False, "Seed not in array")

    # Check if the seed is already in the array
    if seed not in current_seeds:
        return (False, "Seed not in array")

    # Else remove the seed from the array
    current_seeds.remove(seed)

    try:
        # Update the array in the database
        await postgres_client.execute(
            "UPDATE seed_urls SET seeds = $1 WHERE url = $2", current_seeds, url
        )

        return (True, "Seed deleted successfully")

    except Exception as e:
        print("Failed to update url with error:", e)

        return (False, "Failed to delete seed from url")


async def update_seed_url_seed(
    old_seed: str,
    new_seed: str,
    url: str,
    postgres_client: asyncpg.Connection,
):
    """
    Updates a seed that's stored against an url in the database. The seeds are basically
    the initial pages to crawl associated with that url.
    """
    # Get the current array of seeds for the url
    current_seeds = await postgres_client.fetchrow(
        "SELECT seeds FROM seed_urls WHERE url = $1", url
    )

    # Get the current seeds list
    current_seeds = current_seeds[0]

    # Check if the seed is already in the array
    if old_seed not in current_seeds:
        return (False, "Seed not in array")

    # Else get the current index of the old seed
    old_index = current_seeds.index(old_seed)

    # And replace it with the new one
    current_seeds[old_index] = new_seed

    try:
        # Update the array in the database
        await postgres_client.execute(
            "UPDATE seed_urls SET seeds = $1 WHERE url = $2", current_seeds, url
        )

        return (True, "Seed updated successfully")

    except Exception as e:
        print("Failed to update url with error:", e)

        return (False, f"Failed to update seed url with error: {e}")


async def get_seed_urls(
    postgres_client: asyncpg.Connection,
) -> list[SeedUrl]:
    """
    Gets a list of seed urls from the database.

    Parameters
    ----------
    postgres_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    list[SeedUrl]
        A list of seed urls.
    """
    # Get the seed urls from the database
    results = await postgres_client.fetch("SELECT * FROM seed_urls")

    # Convert the results to a list of urls
    urls = [SeedUrl(url=result[1], seeds=result[2]) for result in results]

    return urls


async def get_crawled_urls(
    postgres_client: asyncpg.Connection,
) -> list[CrawledUrl]:
    """
    Gets a list of all the crawled urls from the database.

    Parameters
    ----------
    postgres_client : asyncpg.Connection
        The PostgreSQL client to use.

    Returns
    -------
    list[CrawledUrl]
        A list of crawled urls.
    """

    # Get the crawled urls from the database
    results = await postgres_client.fetch("SELECT * FROM resources")

    # Convert the results to a list of urls
    urls = [
        CrawledUrl(
            url=result[1],
            firstVisited=result[2],
            lastVisited=result[3],
            allVisits=result[4],
            externalLinks=result[5],
        )
        for result in results
    ]

    return urls


async def get_potential_urls(
    postgres_client: asyncpg.Connection,
) -> list[PotentialUrl]:
    """
    Gets a list of all the potential urls from the database.

    Parameters
    ----------
    postgres_client : asyncpg.Connection
        The PostgreSQL client to access the database with the urls
        in.

    Returns
    -------
    list[PotentialUrl]
        A list of potential urls.
    """

    # Get the potential urls from the database
    results = await postgres_client.fetch("SELECT * FROM potential_urls")

    # Convert the results to a list of urls
    urls = [
        PotentialUrl(
            url=result[1],
            firstSeen=result[2],
            timesSeen=result[3],
        )
        for result in results
    ]

    return urls
