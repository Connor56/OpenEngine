import pytest
import storage as st
import qdrant_client
import numpy as np
from qdrant_client.models import VectorParams, Distance


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
    client = qdrant_client.QdrantClient(":memory:")
    client.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=5, distance=Distance.COSINE),
    )

    stored = await st.store_embedding(
        vector=vector,
        metadata=metadata,
        db_client=client,
    )
    assert stored is True

    # Check the vector and metadata were stored correctly
    points = client.scroll(
        collection_name="embeddings",
        with_payload=True,
        with_vectors=True
    )[0]

    assert len(points) == 1
    assert points[0].id == 0
    assert points[0].vector == (vector/np.linalg.norm(vector)).astype(np.float32).tolist()
    assert points[0].payload["text"] == metadata


async def test_log_resource():
    """
    Checks that the log_resource function correctly logs information
    about a resource to the postgres database.
    """