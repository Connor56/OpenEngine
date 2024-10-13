import pytest
import app.core.storage as st
import qdrant_client
import numpy as np
from qdrant_client.models import VectorParams, Distance
from datetime import datetime
from app.models.data_types import CrawledUrl, PotentialUrl


@pytest.mark.asyncio
async def test_store_embedding():
    """
    Test the store_embedding function correctly stores a vector and
    metadata in an in-memory qdrant database.
    """
    # Create a vector and metadata
    vector = np.array([1, 2, 3, 4, 5])
    metadata = {"test": "example meta"}

    # Create a Qdrant client
    client = qdrant_client.AsyncQdrantClient(":memory:")
    await client.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=5, distance=Distance.COSINE),
    )

    # Stores the embedding and metadata
    stored = await st.store_embedding(
        vector=vector,
        metadata=metadata,
        vector_client=client,
    )
    assert stored is True

    # Check the vector and metadata were stored correctly
    points = await client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )
    points = points[0]

    assert len(points) == 1
    assert (
        points[0].vector
        == (vector / np.linalg.norm(vector)).astype(np.float32).tolist()
    )
    assert points[0].payload["text"] == metadata


@pytest.mark.asyncio
async def test_store_two_embedding(vector_client):
    """
    Test the store_embedding function correctly stores two vectors and
    metadata via two separate function calls.
    """

    # Create a vector and metadata
    generator = np.random.default_rng(seed=0)
    vector1 = generator.random(384)
    metadata1 = {"test": "meta1"}

    # Stores the embedding and metadata
    stored = await st.store_embedding(
        vector=vector1,
        metadata=metadata1,
        vector_client=vector_client,
    )
    assert stored is True

    # Create a second vector and metadata
    vector2 = generator.random(384)
    metadata2 = {"test": "meta2"}

    # Stores the embedding and metadata
    stored = await st.store_embedding(
        vector=vector2,
        metadata=metadata2,
        vector_client=vector_client,
    )

    assert stored is True

    # Check the vector and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )
    points = points[0]

    assert len(points) == 2

    # Get the indexes of the vectors 1 and 2
    # This must be done because order is based on randomly assigned uuids and thus is
    # not guaranteed
    idx1 = [
        idx
        for idx, point in enumerate(points)
        if point.payload == {"text": metadata1}
    ][0]
    idx2 = 0 if idx1 == 1 else 1

    # Check the vectors and payload are as expected
    assert (
        points[idx1].vector
        == (vector1 / np.linalg.norm(vector1)).astype(np.float32).tolist()
    )
    assert points[idx1].payload["text"] == metadata1
    assert (
        points[idx2].vector
        == (vector2 / np.linalg.norm(vector2)).astype(np.float32).tolist()
    )
    assert points[idx2].payload["text"] == metadata2


@pytest.mark.asyncio
async def test_log_resource(empty_postgres_client):
    """
    Checks that the log_resource function correctly logs information
    about a searched resource to the postgres database.
    """
    # Create a resource
    the_time = datetime.now()
    resource = st.Resource(
        url="https://example.com",
        firstVisited=the_time,
        lastVisited=the_time,
        allVisits=1,
        externalLinks=[],
    )

    # Get the postgres client
    db_client = empty_postgres_client

    # Log the resource
    await st.log_resource(resource, db_client)

    # Get the resource from the database
    results = await db_client.fetch("SELECT * FROM resources")

    # Was it added correctly?
    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == "https://example.com"
    assert results[0][4] == 1
    assert results[0][5] == []


@pytest.mark.asyncio
async def test_add_seed_url(empty_postgres_client):
    """
    Tests a seed url can be added correctly to the database.
    """

    url = "https://example.com"

    # Add the url to the database
    await st.add_seed_url(url, empty_postgres_client)

    # Get the resource from the database
    results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

    print(results)

    # Was it added correctly?
    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == url


@pytest.mark.asyncio
async def test_delete_seed_url(empty_postgres_client):
    """
    Tests a seed url can be deleted correctly from the database.
    """

    url = "https://example.com"

    # Add the url to the database
    assert await st.add_seed_url(url, empty_postgres_client)

    # Delete the url from the database
    await st.delete_seed_url(url, empty_postgres_client)

    # Get the resource from the database
    results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

    # Was it added correctly?
    assert len(results) == 0


@pytest.mark.asyncio
async def test_update_seed_url(empty_postgres_client):
    """
    Check that the update_seed_url function correctly updates a seed
    url in the database.
    """

    url = "https://example.com"

    # Add the url to the database
    assert await st.add_seed_url(url, empty_postgres_client)

    # Update the url in the database
    await st.update_seed_url(
        url, "https://snowchild.com", empty_postgres_client
    )

    # Get the resource from the database
    results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

    # Was it added correctly?
    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == "https://snowchild.com"


@pytest.mark.asyncio
async def test_get_seed_urls(empty_postgres_client):
    """
    Check that the get_seed_urls function correctly returns a list of
    seed urls from the database.
    """

    # List of urls to add to the database
    urls_to_add = [
        "https://example.com",
        "https://snowchild.com",
        "https://casey.com",
    ]

    # Add the seed urls to the database
    for url in urls_to_add:
        assert await st.add_seed_url(url, empty_postgres_client)

    # Get the seed urls
    results = await st.get_seed_urls(empty_postgres_client)

    # Check the urls are correct
    assert len(results) == len(urls_to_add)

    # Put urls to add into the expected format
    urls_to_add = [{"url": url} for url in urls_to_add]

    assert results == urls_to_add


@pytest.mark.asyncio
async def test_get_crawled_urls(empty_postgres_client):
    """
    Check that the get_searchable_urls function correctly returns a
    list of seed urls from the database.
    """

    # List of urls to add to the database
    urls_to_add = [
        "https://example.com",
        "https://snowchild.com",
        "https://casey.com",
    ]

    the_time = datetime.now()

    # Add the seed urls to the database
    for url in urls_to_add:
        # Create a resource
        resource = st.Resource(
            url=url,
            firstVisited=the_time,
            lastVisited=the_time,
            allVisits=1,
            externalLinks=[],
        )
        assert await st.log_resource(resource, empty_postgres_client)

    # Get the searchable urls
    results: list[CrawledUrl] = await st.get_crawled_urls(empty_postgres_client)

    # Check the urls are correct
    assert len(results) == len(urls_to_add)

    for idx, result in enumerate(results):
        assert result.url in urls_to_add[idx]
        assert result.firstVisited is not None
        assert result.lastVisited is not None
        assert result.allVisits == 1
        assert result.externalLinks == []


@pytest.mark.asyncio
async def test_add_potential_url(empty_postgres_client):
    """
    Checks that the add_potential_urls function correctly adds a
    potential url to the database.
    """

    url = "https://example.com"
    time_seen = datetime.now()

    # Add the url to the database
    assert await st.add_potential_url(url, time_seen, empty_postgres_client)

    # Get the resource from the database
    results = await empty_postgres_client.fetch("SELECT * FROM potential_urls")

    # Was it added correctly?
    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == url
    assert results[0][2] == time_seen
    assert results[0][3] == 1

    # Attempt to add the same url again
    assert await st.add_potential_url(url, time_seen, empty_postgres_client)

    # Check this increments the timesSeen column
    results = await empty_postgres_client.fetch("SELECT * FROM potential_urls")

    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == url
    assert results[0][2] == time_seen
    assert results[0][3] == 2

@pytest.mark.asyncio
