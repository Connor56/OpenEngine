import pytest
import pytest_asyncio
from datetime import datetime
import http.server
import socketserver
import threading
from pathlib import Path
import asyncpg
from typing import Tuple
import requests
import time


# Fixture to start and stop the local HTTP server
@pytest.fixture(scope="session")
def local_site():
    # Define the directory where the HTML files are located
    location = "test_data/simple_site"
    site_directory = (
        Path(__file__).parent / location
    )  # Folder containing your HTML files

    print("Site directory is:", site_directory)

    # Check if the directory exists
    if not site_directory.exists():
        raise RuntimeError(f"Directory {site_directory} does not exist")

    # Define the handler to serve the directory
    handler = http.server.SimpleHTTPRequestHandler
    # handler.directory = str(site_directory)  # Set the directory to serve files from

    # Define the server (localhost with a random available port)
    with socketserver.TCPServer(("", 0), handler) as httpd:
        port = httpd.server_address[1]  # Get the port number
        server_url = f"http://localhost:{port}/tests/app_tests/{location}"

        # Start the server in a new thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        response = requests.get(server_url, timeout=1)
        if response.status_code != 200:
            raise RuntimeError("Failed to start local server")

        # Yield the URL to be used in tests
        yield server_url

        # Shut down the server after the test
        httpd.shutdown()
        server_thread.join()


@pytest.fixture(scope="session")
def base_postgres_details():
    """
    A fixture that sets up a postgres database to be connected to
    during testing.
    """
    from tests.app_tests.setup_postgres import (
        start_ephemeral_postgres,
        stop_ephemeral_postgres,
    )

    try:
        # Start a temporary PostgreSQL server
        print("starting postgres")
        temp_dir, port = start_ephemeral_postgres()

        yield port

    finally:
        print("cleaning up")

        stop_ephemeral_postgres(temp_dir)


@pytest_asyncio.fixture(scope="function")
async def empty_postgres_client(base_postgres_details: str):
    """
    A fixture that puts an empty resources table into the postgres
    client and provides it for testing. Then drops the table once
    the function is complete.
    """

    # Get the port details
    port = base_postgres_details

    try:
        # Connect to the temporary PostgreSQL server
        client = await asyncpg.connect(
            database="postgres",
            user="postgres",
            host="localhost",
            port=port,
        )

        print("connected to postgres")

        # Create the table
        table_sql = """CREATE TABLE resources ( 
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            firstVisited TIMESTAMP NOT NULL,
            lastVisited TIMESTAMP NOT NULL,
            allVisits INT DEFAULT 1,
            externalLinks TEXT[]
        );"""

        await client.execute(table_sql)

        yield client

    finally:

        await client.execute("DROP TABLE resources")

        await client.close()


@pytest_asyncio.fixture(scope="function")
async def populated_postgres_client(base_postgres_details: str):
    """
    A fixture that provides a psycopg2 client for testing and a the function for killing
    the server once the user is complete.
    """

    # Get the port details
    port = base_postgres_details

    try:
        # Connect to the temporary PostgreSQL server
        client = await asyncpg.connect(
            database="postgres",
            user="postgres",
            host="localhost",
            port=port,
        )

        print("connected to postgres")

        # Create the table
        table_sql = """CREATE TABLE resources ( 
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            firstVisited TIMESTAMP NOT NULL,
            lastVisited TIMESTAMP NOT NULL,
            allVisits INT DEFAULT 1,
            externalLinks TEXT[]
        );"""

        await client.execute(table_sql)

        # Insert a resource
        await client.execute(
            "INSERT INTO resources (url, firstVisited, lastVisited, allVisits, externalLinks) VALUES (%s, %s, %s, %s, %s)",
            (
                "https://caseyhandmer.wordpress.com/",
                datetime.now(),
                datetime.now(),
                1,
                [],
            ),
        )

        yield client

    finally:

        await client.execute("DROP TABLE resources")

        await client.close()


@pytest.fixture(scope="session")
def base_vector_client():
    """
    A fixture that provides a base qdrant client in memory that's used
    throughout the tests.
    """
    from qdrant_client import AsyncQdrantClient

    client = AsyncQdrantClient(":memory:")

    yield client

    client.close()
    del client


@pytest_asyncio.fixture(scope="function")
async def vector_client(base_vector_client):
    """
    A fixture that provides a Qdrant client with the embeddings collection
    for testing. That is cleaned once the function is complete.
    """
    from qdrant_client.models import VectorParams, Distance

    await base_vector_client.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    yield base_vector_client

    await base_vector_client.delete_collection("embeddings")


@pytest_asyncio.fixture(scope="function")
async def search_vector_client(base_vector_client):
    """
    A fixture that provides a Qdrant client with the embeddings collection
    populated with test data crawled from CJ Handmer's blog.
    """
    from qdrant_client.models import VectorParams, Distance
    from joblib import load

    await base_vector_client.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    vectors = load("test_data/search_data/qdrant_vectors.joblib")
    await base_vector_client.upsert(
        collection_name="embeddings",
        points=vectors,
        wait=True,
    )

    yield base_vector_client

    await base_vector_client.delete_collection("embeddings")


@pytest.fixture(scope="session")
def embedding_model():
    """
    A fixture that provides a sentence_transformers model for testing.
    """
    import sentence_transformers

    return sentence_transformers.SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


@pytest.fixture(scope="function")
def soup():
    """
    A fixture that provides a BeautifulSoup object for testing.
    """
    from bs4 import BeautifulSoup
    from joblib import load

    soup = load("test_data/html_page.joblib")
    return soup
