import pytest
import app.core.search as search
import time


@pytest.mark.asyncio
async def test_get_top_matches(
    search_vector_client,
    embedding_model,
):
    """
    Test the correct urls are returned to the search function.
    """

    query = "What's the best form of energy available to every consumer in the world?"

    top_urls = await search.get_top_matches(
        query,
        embedding_model,
        search_vector_client,
        None,
    )

    for key, value in top_urls:
        print(key, value)

    assert False


@pytest.mark.asyncio
async def test_fetch_matches(search_vector_client, embedding_model):
    """
    Tests the fetch_matches function correctly returns the closest matches.
    """

    # Embed some text
    search_vector = embedding_model.encode(
        "What's the best form of energy available to every consumer in the world?",
        convert_to_numpy=True,
    )

    start = time.time()

    # Get the matches
    matches = await search.fetch_matches(search_vector_client, search_vector)

    print("Time taken:", time.time() - start)

    # Get the urls and scores
    urls = [m.payload["text"]["url"] for m in matches]

    scores = [m.score for m in matches]

    # Check url order
    assert (
        urls[0]
        == "https://caseyhandmer.wordpress.com/2024/05/22/the-solar-industrial-revolution-is-the-biggest-investment-opportunity-in-history"
    )
    assert (
        urls[1]
        == "https://caseyhandmer.wordpress.com/2024/05/22/the-solar-industrial-revolution-is-the-biggest-investment-opportunity-in-history"
    )
    assert (
        urls[2]
        == "https://caseyhandmer.wordpress.com/2021/04/25/powering-the-lunar-base"
    )

    # Check score order
    assert round(scores[0], 6) == 0.529455
    assert round(scores[1], 6) == 0.517381
    assert round(scores[2], 6) == 0.515256
