"""
Description:
    Processes responses collected by the crawler, turning them into
    embeddings, and other metadata used for searching.

Created:
    2024-09-14
"""

from bs4 import BeautifulSoup
import re
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import sentence_transformers
from dataclasses import dataclass
from typing import Optional
from storage import store_embedding, Resource, log_resource
import asyncio
from psycopg2.extensions import connection
from datetime import datetime
from urllib.parse import urlparse


@dataclass
class Response:
    type: str
    soup: BeautifulSoup
    url: str
    url_id: int = -1


async def process(
    response_queue: asyncio.Queue,
    model: sentence_transformers.SentenceTransformer,
    vector_client: QdrantClient,
    db_client: connection,
    pause: asyncio.Event,
    end: asyncio.Event,
    max_iter: Optional[int] = -1,
):
    """
    Processes responses collected by the crawler, turning them into
    embeddings, and other metadata used for searching.
    """
    num_iter = 0
    while not pause.is_set():
        # Crawler ended?
        if end.is_set():
            break

        if max_iter != -1 and num_iter >= max_iter:
            break
        else:
            num_iter += 1

        # Get response from queue
        response: Response = await response_queue.get()
        response_queue.task_done()

        if response.type == "webpage":
            soup = response.soup

            # Process webpage
            vectors, metadata = await process_html_to_vectors(
                soup, model, vector_client
            )

            # Store the vectors and metadata
            vectors = vectors.tolist()
            metadata = [metadata] * len(vectors)

            await store_embedding(vectors, metadata, vector_client)

            # Get the base site
            base_site = get_base_site(response.url)

            # Get all the external links
            links = soup.find_all("a")
            drop_strings = [""]
            first_letter_drops = ["#", "/"]
            links = [
                link["href"]
                for link in links
                if base_site not in link["href"]
                and link["href"] not in drop_strings
                and link["href"][0] not in first_letter_drops
            ]

            # TODO: Setup a swtich statement or function for this that checks if the
            # resource is already present in the database before adding it.
            # Log a new resource
            if response.url_id == -1:
                # Create a new resource
                resource = Resource(
                    url=response.url,
                    firstVisited=datetime.now(),
                    lastVisited=datetime.now(),
                    allVisits=1,
                    externalLinks=links,
                )

                await log_resource(resource, db_client)


async def process_html_to_vectors(
    soup: BeautifulSoup,
    model: sentence_transformers.SentenceTransformer,
    db_client: QdrantClient,
    max_length: int = 450,
) -> None:
    """
    Processes a BeautifulSoup object into a list of sentences and turns each of them
    into a vector using the sentence_transformers model. Puts the vectors into a Qdrant
    collection.

    This is test code for now.
    """
    # Extract visible text from the soup
    visible_text = extract_visible_text(soup)

    # Get splits of 450 words
    split_text = visible_text.split(" ")
    splits = list(range(0, len(split_text), max_length))
    splits.append(len(split_text))

    # Create the sequences
    sequences = [
        " ".join(split_text[i:j]) for i, j in zip(splits[:-1], splits[1:])
    ]

    # Turns the sequences into float16 vectors
    vectors = model.encode(sequences, convert_to_numpy=True)
    vectors = vectors.astype(np.float32)

    metadata = {}

    return vectors, metadata


def extract_visible_text(
    soup: BeautifulSoup,
):
    """
    Extracts the visible text fro a webpage that's stored as a BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        The BeautifulSoup object to extract the visible text from.

    Returns
    -------
    str
        The visible text.
    """
    # Remove elements that do not contain user-visible text
    for element in soup(
        ["script", "style", "meta", "header", "footer", "nav", "noscript"]
    ):
        element.decompose()

    # Extract the raw text
    raw_text = soup.get_text(separator=" ")

    # Clean up the extracted text
    visible_text = re.sub(
        r"\s+", " ", raw_text
    ).strip()  # Replaces multiple spaces/newlines with a single space

    return visible_text


def get_base_site(
    url: str,
) -> str:
    """
    Extracts the base site location from an U

    Parameters
    ----------
    url : str
        The URL to extract the base URL from.

    Returns
    -------
    str
        The base URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc
