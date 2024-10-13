"""
Description:
    Utility functions for the crawler and processor.

Created:
    2024-09-26
"""

from urllib.parse import urlparse, urlunparse
from typing import List


def clean_urls(
    urls: List[str],
):
    """
    Cleans a list of urls by removing fragments and trailing slashes,
    and adds them to a set to ensure no duplicates. Returns these
    urls.
    """

    # Filter urls that are None
    urls = [url for url in urls if url is not None]

    cleaned_urls = set()

    # Remove fragments and trailing slashes
    for url in urls:

        parsed_url = urlparse(url)

        cleaned_url = parsed_url._replace(fragment="", query="", params="")

        final_url = urlunparse(cleaned_url).rstrip("/")

        cleaned_urls.add(final_url)

    return list(cleaned_urls)


def handle_relative_url(
    urls: str | List[str],
    current_url: str,
    base_site: str,
) -> str:
    """
    Turns a relative url into an absolute url.
    """
    if not isinstance(urls, list):
        urls = [urls]

    for idx, url in enumerate(urls):
        # Get the parsed url
        parsed_url = urlparse(url)

        # Skip empty urls
        if url == "":
            continue

        # Add the base site to internal links
        if url[0] == "/":
            urls[idx] = base_site + url

        # Create a relative absolute url
        elif not parsed_url.scheme and not parsed_url.netloc:
            url_pos = current_url.split("/")[:-1]
            url_pos += url.split("/")
            urls[idx] = "/".join(url_pos)

    return urls


def get_base_site(
    url: str,
) -> str:
    """
    Extracts the base site location from an Url.

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
