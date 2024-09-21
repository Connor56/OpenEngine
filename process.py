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

@dataclass
class Response:
    type: str
    soup: BeautifulSoup
    url: str


async def process(response_queue, model, vector_client, pause, end):
    """
    Processes responses collected by the crawler, turning them into
    embeddings, and other metadata used for searching.
    """
    while not pause.is_set():
        # Crawler ended?
        if end.is_set():
            break
        
        # Get response from queue
        response: Response = await response_queue.get()
        response_queue.task_done()
        
        if response.type == "webpage":
            # Process webpage
            soup = response.soup
            vector, metadata = await process_html_to_vectors(soup, model, vector_client)


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


def extract_visible_text(soup):
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
