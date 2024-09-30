import pytest
import app.core.storage as st
import qdrant_client
import numpy as np
from qdrant_client.models import VectorParams, Distance
from datetime import datetime


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
        idx for idx, point in enumerate(points) if point.payload == {"text": metadata1}
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
