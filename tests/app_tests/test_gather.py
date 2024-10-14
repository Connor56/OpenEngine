import pytest
import app.core.gather as gather
from qdrant_client.models import VectorParams, Distance
import datetime
import app.core.storage as st
import asyncio


@pytest.mark.asyncio
async def test_gather(
    empty_postgres_client,
    vector_client,
    embedding_model,
    local_site,
):
    """
    Test the gather function correctly crawls a website and returns
    links on the page.
    """

    # Get the local site url to crawl
    server_url = local_site + "/page1.html"

    print(server_url)

    # Get the postgres client
    db_client = empty_postgres_client

    # Store the url in the postgres database
    stored = await st.log_resource(
        resource=st.Resource(
            url=server_url,
            firstVisited=datetime.datetime.now(),
            lastVisited=datetime.datetime.now(),
            allVisits=1,
            externalLinks=[],
        ),
        db_client=db_client,
    )

    assert stored

    # Set up asyncio events
    pause = asyncio.Event()
    end = asyncio.Event()

    await gather.gather(
        vector_client,
        db_client,
        embedding_model,
        revisit_delta=datetime.timedelta(microseconds=0),
        max_iter=4,
        regex_patterns=["https://", "http://"],
        pause=pause,
        end=end,
    )

    # Check the vectors and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )

    points = points[0]

    assert len(points) == 4

    # Check the database has the correct number of resources
    results = await db_client.fetch("SELECT * FROM resources")
    assert len(results) == 5

    # Check the set of urls stored is the same
    vector_urls = [p.payload["text"]["url"] for p in points]
    db_urls = [r[1] for r in results]
    assert set(vector_urls) == set(db_urls)

    # Check the links and the urls are correct
    assert results[1][1] == server_url
    assert results[1][5][0] == f"{local_site}/page2.html"

    assert results[2][1] == f"{local_site}/page2.html"
    assert results[2][5][0] == f"{local_site}/page1.html"


@pytest.mark.asyncio
async def test_pausing_gather(
    empty_postgres_client,
    vector_client,
    embedding_model,
    local_site,
):
    """
    Test the gather function correctly crawls a website and returns
    links on the page.
    """

    # Get the local site url to crawl
    server_url = local_site + "/page1.html"

    print(server_url)

    # Get the postgres client
    db_client = empty_postgres_client

    # Store the url in the postgres database
    assert await st.log_resource(
        resource=st.Resource(
            url=server_url,
            firstVisited=datetime.datetime.now(),
            lastVisited=datetime.datetime.now(),
            allVisits=1,
            externalLinks=[],
        ),
        db_client=db_client,
    )

    # Set up asyncio events
    pause = asyncio.Event()
    end = asyncio.Event()

    # Set up the crawler
    gather_task = asyncio.create_task(
        gather.gather(
            vector_client,
            db_client,
            embedding_model,
            revisit_delta=datetime.timedelta(microseconds=0),
            max_iter=4,
            regex_patterns=["https://", "http://"],
            pause=pause,
            end=end,
        )
    )

    pause.set()

    # Pause the crawler
    print("Paused", pause.is_set())

    await asyncio.sleep(1)

    # Un pause the crawler
    pause.set()

    # Pause the crawler
    print("Paused", pause.is_set())

    await asyncio.sleep(5)

    end.set()

    # await gather_task

    # Check the vectors and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )

    points = points[0]

    assert len(points) == 4

    # Check the database has the correct number of resources
    results = await db_client.fetch("SELECT * FROM resources")
    assert len(results) == 5

    # Check the set of urls stored is the same
    vector_urls = [p.payload["text"]["url"] for p in points]
    db_urls = [r[1] for r in results]
    assert set(vector_urls) == set(db_urls)

    # Check the links and the urls are correct
    assert results[1][1] == server_url
    assert results[1][5][0] == f"{local_site}/page2.html"

    assert results[2][1] == f"{local_site}/page2.html"
    assert results[2][5][0] == f"{local_site}/page1.html"
