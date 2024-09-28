import pytest
import process
import asyncio
from bs4 import BeautifulSoup


@pytest.mark.asyncio
async def test_process(
    embedding_model,
    soup,
    vector_client,
    empty_postgres_client,
):
    """
    Test the process function correctly crawls a website and returns
    links on the page.
    """

    # Create an event to pause the crawler
    pause = asyncio.Event()

    # Create an event to end the crawler
    end = asyncio.Event()

    # Create a queue for the processor
    response_queue = asyncio.Queue()

    # Add a response to the queue
    await response_queue.put(
        process.Response(
            type="webpage", soup=soup, url="https://caseyhandmer.wordpress.com/"
        )
    )

    # Start the process
    await process.process(
        response_queue,
        embedding_model,
        vector_client,
        empty_postgres_client,
        pause,
        end,
        max_iter=1,
    )

    # Check the queue is empty
    assert response_queue.empty()

    all_entries = await vector_client.scroll(
        collection_name="embeddings", with_vectors=True
    )

    # Check 4 vectors were added
    assert len(all_entries[0]) == 4

    # Check vector metadata is correct
    assert all_entries[0][0].payload == {
        "text": {"url": "https://caseyhandmer.wordpress.com/"}
    }

    # Check the postgres client has a record
    cursor = empty_postgres_client.cursor()
    cursor.execute("SELECT * FROM resources")
    results = cursor.fetchall()

    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == "https://caseyhandmer.wordpress.com/"
    assert results[0][4] == 1
    assert len(results[0][5]) == 5


@pytest.mark.asyncio
async def test_process_with_empty_links(
    embedding_model,
    vector_client,
    empty_postgres_client,
    mocker,
):
    """
    Test the process function correctly crawls a website and returns
    links on the page.
    """

    # Create an event to pause the crawler
    pause = asyncio.Event()

    # Create an event to end the crawler
    end = asyncio.Event()

    # Create a queue for the processor
    response_queue = asyncio.Queue()

    # mock_response = mocker.Mock()
    mock_response = BeautifulSoup("<html><body><a>Example</a></body></html>")
    mocker.patch("bs4.BeautifulSoup.find_all", return_value=mock_response)

    # Add a response to the queue
    await response_queue.put(
        process.Response(
            type="webpage",
            soup=mock_response,
            url="https://caseyhandmer.wordpress.com/",
        )
    )

    # Start the process
    await process.process(
        response_queue,
        embedding_model,
        vector_client,
        empty_postgres_client,
        pause,
        end,
        max_iter=1,
    )

    # Check the queue is empty
    assert response_queue.empty()

    all_entries = await vector_client.scroll(
        collection_name="embeddings",
        with_vectors=True,
    )

    # Check 1 vector was added
    assert len(all_entries[0]) == 1

    # Check vector metadata is correct
    assert all_entries[0][0].payload == {
        "text": {"url": "https://caseyhandmer.wordpress.com/"}
    }

    # Check the postgres client has a record
    cursor = empty_postgres_client.cursor()
    cursor.execute("SELECT * FROM resources")
    results = cursor.fetchall()

    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == "https://caseyhandmer.wordpress.com/"
    assert results[0][4] == 1
    assert len(results[0][5]) == 0
