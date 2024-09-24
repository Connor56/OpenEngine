import pytest
import asyncio
import gather
import qdrant_client
from qdrant_client.models import VectorParams, Distance
import datetime


@pytest.mark.asyncio
async def test_gather(populated_postgres_client, vector_client, embedding_model):
    """
    Test the gather function correctly crawls a website and returns
    links on the page.
    """

    # Get the postgres client
    db_client = populated_postgres_client

    await gather.gather(vector_client, db_client, embedding_model, revisit_delta=datetime.timedelta(microseconds=0), max_iter=1)

    assert False
