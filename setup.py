from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import asyncpg


async def setup_postgres(ayncpg: asyncpg.Connection):
    client = await asyncpg.connect(
        user="postgres", password="postgres", host="localhost", port=5432
    )

    print("connected to postgres")

    # Create the resource table
    resources_sql = """CREATE TABLE resources ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstVisited TIMESTAMP NOT NULL,
        lastVisited TIMESTAMP NOT NULL,
        allVisits INT DEFAULT 1,
        externalLinks TEXT[],
        timeBetweenVisits INT
    );"""

    await client.execute(resources_sql)

    # Create the admin table
    admins_sql = """CREATE TABLE admins ( 
        id SERIAL PRIMARY KEY,
        username VARCHAR(2048) NOT NULL,
        password VARCHAR(2048) NOT NULL
    );"""

    await client.execute(admins_sql)

    # Create the seed urls table
    seed_urls_sql = """CREATE TABLE seed_urls ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        seeds VARCHAR(512)[],
        timeBetweenVisits INT
    );"""

    await client.execute(seed_urls_sql)

    potential_urls_sql = """CREATE TABLE potential_urls ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstSeen TIMESTAMP NOT NULL,
        timesSeen INT DEFAULT 1
    );"""

    await client.execute(potential_urls_sql)

    print("added all tables")


async def setup_qdrant(qdrant: QdrantClient):
    # Add the embeddings collection if the containers have been restarted
    created = qdrant.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    print("Embeddings collection created:", created)
