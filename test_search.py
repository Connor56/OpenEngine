import pytest
import search
import time


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
    assert scores[0] == 0.5294554233551025
    assert scores[1] == 0.5173807144165039
    assert scores[2] == 0.5152561664581299


@pytest.mark.asyncio
async def test_(search_vector_client, embedding_model):
    pass
