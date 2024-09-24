import pytest
from datetime import datetime


@pytest.fixture(scope="function")
def empty_postgres_client():
    """
    A fixture that provides a psycopg2 client for testing and a the function for killing
    the server once the user is complete.
    """
    import psycopg2
    from setup_postgres import start_ephemeral_postgres, stop_ephemeral_postgres

    try:
        # Start a temporary PostgreSQL server
        print("starting postgres")
        temp_dir, port = start_ephemeral_postgres()

        # Connect to the temporary PostgreSQL server
        client = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host="localhost",
            port=port
        )
        print("connected to postgres")

        cursor = client.cursor()

        # Create the table
        table_sql = """CREATE TABLE resources ( 
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            firstVisited TIMESTAMPTZ NOT NULL,
            lastVisited TIMESTAMPTZ NOT NULL,
            allVisits INT DEFAULT 1,
            externalLinks TEXT[]
        );"""

        cursor.execute(table_sql)

        yield client

        client.close()

    except Exception as e:
        print(e)
        stop_ephemeral_postgres(temp_dir)

    finally:
        print("cleaning up")

        stop_ephemeral_postgres(temp_dir)


@pytest.fixture(scope="function")
def populated_postgres_client():
    """
    A fixture that provides a psycopg2 client for testing and a the function for killing
    the server once the user is complete.
    """
    import psycopg2
    from setup_postgres import start_ephemeral_postgres, stop_ephemeral_postgres

    try:
        # Start a temporary PostgreSQL server
        print("starting postgres")
        temp_dir, port = start_ephemeral_postgres()

        # Connect to the temporary PostgreSQL server
        client = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host="localhost",
            port=port
        )
        print("connected to postgres")

        cursor = client.cursor()

        # Create the table
        table_sql = """CREATE TABLE resources ( 
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            firstVisited TIMESTAMP NOT NULL,
            lastVisited TIMESTAMP NOT NULL,
            allVisits INT DEFAULT 1,
            externalLinks TEXT[]
        );"""

        cursor.execute(table_sql)

        # Insert a resource
        cursor.execute(
            "INSERT INTO resources (url, firstVisited, lastVisited, allVisits, externalLinks) VALUES (%s, %s, %s, %s, %s)",
            ("https://caseyhandmer.wordpress.com/", datetime.now(), datetime.now(), 1, [])
        )

        yield client

        client.close()

    except Exception as e:
        print(e)
        stop_ephemeral_postgres(temp_dir)

    finally:
        print("cleaning up")

        stop_ephemeral_postgres(temp_dir)


@pytest.fixture(scope="function")
def vector_client():
    """
    A fixture that provides a Qdrant client with the embeddings collection
    for testing.
    """
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance

    client = QdrantClient(":memory:")
    client.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    return client


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