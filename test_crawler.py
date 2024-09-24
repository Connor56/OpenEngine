import pytest
import asyncio
import httpx
import crawl


def test_crawler():
    """
    Test the crawler function correctly crawls a website and returns
    links on the page.
    """
    pass


@pytest.mark.asyncio
async def test_crawler_link_filter(mocker):
    """
    Test the crawler function and a standard pattern filter correctly
    crawls a website and returns links from a page.
    """

    # Set up mock response for httpx.AsyncClient.get
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 200
    mock_response.text = (
        '<html><body><a href="https://example.com">Example</a></body></html>'
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    url_queue = asyncio.Queue()
    response_queue = asyncio.Queue()
    pause_crawling = asyncio.Event()
    stop_crawling = asyncio.Event()
    await url_queue.put("https://caseyhandmer.wordpress.com/")

    async with httpx.AsyncClient() as client:
        await crawl.crawler(
            url_queue,
            url_filter={
                "filter_func": crawl.pattern_filter,
                "kwargs": {"regex_patterns": ["https://"]},
            },
            client=client,
            response_queue=response_queue,
            pause=pause_crawling,
            end=stop_crawling,
            max_iter=1,
        )

    # Check url queue outputs
    assert not url_queue.empty()
    assert url_queue.qsize() == 1
    assert list(url_queue._queue) == ["https://example.com"]

    # Check response queue outputs
    assert not response_queue.empty()
    assert response_queue.qsize() == 1
    response_text = str(list(response_queue._queue)[0])
    assert response_text == mock_response.text


@pytest.mark.asyncio
async def test_crawler_seen_urls(mocker):
    """
    Test the crawler function won't add an url that has already been
    seen.
    """

    # Set up mock response for httpx.AsyncClient.get
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 200
    mock_response.text = (
        '<html><body><a href="https://example.com">Example</a></body></html>'
    )
    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    url_queue = asyncio.Queue()
    response_queue = asyncio.Queue()
    pause_crawling = asyncio.Event()
    stop_crawling = asyncio.Event()
    await url_queue.put("https://caseyhandmer.wordpress.com/")

    async with httpx.AsyncClient() as client:
        await crawl.crawler(
            url_queue,
            url_filter={
                "filter_func": crawl.pattern_filter,
                "kwargs": {"regex_patterns": ["https://"]},
            },
            client=client,
            response_queue=response_queue,
            pause=pause_crawling,
            end=stop_crawling,
            max_iter=1,
            seen_urls=["https://example.com"],
        )

    # Check url queue outputs
    assert url_queue.empty()
    assert url_queue.qsize() == 0
    assert list(url_queue._queue) == []


def test_clean_urls():
    """
    Test the clean_urls function correctly cleans a list of urls.
    """
    urls = [
        "https://example.com",
        "https://example.com/example",
        "https://example.com/example/",
        "https://example.com/#example",
        "https://example.com/#example/",
        "https://example.com/#example/example",
    ]

    cleaned_urls = crawl.clean_urls(urls)

    assert len(cleaned_urls) == 2
    assert set(cleaned_urls) == set([
        "https://example.com",
        "https://example.com/example",
    ])
