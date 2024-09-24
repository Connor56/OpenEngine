import pytest
import process
import asyncio


@pytest.mark.asyncio
async def test_process(embedding_model, soup, vector_client, empty_postgres_client):
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
    await response_queue.put(process.Response(type="webpage", soup=soup, url="https://caseyhandmer.wordpress.com/"))

    # Start the process
    await process.process(response_queue, embedding_model, vector_client, empty_postgres_client, pause, end, max_iter=1)

    # Check the queue is empty
    assert response_queue.empty()
    
    all_entries = vector_client.scroll(collection_name="embeddings", with_vectors=True)
    
    # Check 4 vectors were added
    assert len(all_entries[0]) == 4

    # Check vector metadata is correct
    assert all_entries[0][0].payload == {"text": {}}

    # Check the postgres client has a record
    cursor = empty_postgres_client.cursor()
    cursor.execute("SELECT * FROM resources")
    results = cursor.fetchall()

    assert len(results) == 1
    assert results[0][0] == 1
    assert results[0][1] == "https://caseyhandmer.wordpress.com/"
    assert results[0][4] == 1
    assert len(results[0][5]) == 6


def test_get_base_site():
    """
    Test the get_base_site function correctly extracts the base site
    from a URL.
    """
    base_site = process.get_base_site("https://caseyhandmer.wordpress.com/some/random/path#an_id")
    expected_base_site = "https://caseyhandmer.wordpress.com"
    assert base_site == expected_base_site

