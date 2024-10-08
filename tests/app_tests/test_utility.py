import pytest
import app.core.utility as utility


def test_clean_urls():
    """
    Test the clean_urls function correctly cleans a list of urls. Of
    meaningless url endings.
    """
    urls = [
        "https://example.com",
        "https://example.com/example",
        "https://example.com/example/",
        "https://example.com/#example",
        "https://example.com/#example/",
        "https://example.com/#example/example",
        "https://example.com/example?query=1",
    ]

    cleaned_urls = utility.clean_urls(urls)

    assert len(cleaned_urls) == 2
    assert set(cleaned_urls) == set(
        [
            "https://example.com",
            "https://example.com/example",
        ]
    )


def test_clean_urls_removes_none():
    """
    None's can appear in the urls list, so need to make sure they are
    removed.
    """
    urls = [None]
    cleaned_urls = utility.clean_urls(urls)
    assert cleaned_urls == []


def test_handle_relative_url():
    """
    Test the handle_relative_url function correctly handles relative
    urls.
    """
    current_url = "https://caseyhandmer.wordpress.com/test_data/simple_site/page1.html"
    base_site = "https://caseyhandmer.wordpress.com"

    # Test relative url
    relative_url = "/page2.html"
    expected_url = "https://caseyhandmer.wordpress.com/page2.html"
    assert (
        utility.handle_relative_url(relative_url, current_url, base_site)[0]
        == expected_url
    )

    # Test relative url with query string
    relative_url = "page2.html"
    expected_url = "https://caseyhandmer.wordpress.com/test_data/simple_site/page2.html"
    assert (
        utility.handle_relative_url(relative_url, current_url, base_site)[0]
        == expected_url
    )


def test_handle_relative_url():
    """
    Test the handle_relative_url function correctly deals with
    empty string urls
    """
    current_url = "https://caseyhandmer.wordpress.com/test_data/simple_site/page1.html"
    base_site = "https://caseyhandmer.wordpress.com"

    relative_url = ""
    expected_url = ""
    assert (
        utility.handle_relative_url(relative_url, current_url, base_site)[0]
        == expected_url
    )


def test_get_base_site():
    """
    Test the get_base_site function correctly extracts the base site
    from a URL.
    """
    base_site = utility.get_base_site(
        "https://caseyhandmer.wordpress.com/some/random/path#an_id"
    )
    expected_base_site = "https://caseyhandmer.wordpress.com"
    assert base_site == expected_base_site
