import pytest
import storage as st
import qdrant_client
import numpy as np
from qdrant_client.models import VectorParams, Distance
from datetime import datetime
import psycopg2
from setup_postgres import start_ephemeral_postgres, stop_ephemeral_postgres
import os


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

    # Stores the embedding and metadata
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


@pytest.mark.asyncio
async def test_log_resource():
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

    try:
        print("starting postgres")
        temp_dir, port = start_ephemeral_postgres()
        db_client = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host="localhost",
            port=port
        )
        print("connected to postgres")

        # Create the table
        table_sql = """CREATE TABLE resources ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstVisited TIMESTAMPTZ NOT NULL,
        lastVisited TIMESTAMPTZ NOT NULL,
        allVisits INT DEFAULT 1,
        externalLinks TEXT[]
        );"""

        cursor = db_client.cursor()
        cursor.execute(table_sql)

        # Log the resource
        await st.log_resource(resource, db_client)

        # Get the resource from the database
        cursor.execute("SELECT * FROM resources")
        
        results = cursor.fetchall()

        # Was it added correctly?
        assert len(results) == 1
        assert results[0][0] == 1
        assert results[0][1] == "https://example.com"
        assert results[0][4] == 1
        assert results[0][5] == []

    finally:
        print("cleaning up")
        stop_ephemeral_postgres(temp_dir)
