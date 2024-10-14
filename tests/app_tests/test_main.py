import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app, get_postgres_client, get_admin_page, get_qdrant_client
from app.auth.auth import set_credentials
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio


@pytest.mark.asyncio
async def test_login(empty_postgres_client):
    """
    Test the login endpoint correctly authenticates an admin user, returns
    a valid token, but reject an invalid user.
    """

    # Add an admin user to the postgres database
    assert await set_credentials("admin", "password", empty_postgres_client)

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    # Login with correct credentials
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            "/login",
            json={
                "username": "admin",
                "password": "password",
            },
        )

        # Check the response is correct
        assert response.status_code == 200

        # Check the keys are correct
        response_json = response.json()
        assert response_json.keys() == {"token", "type"}
        assert response_json["type"] == "bearer"

        # Login with incorrect credentials
        response = await ac.post(
            "/login",
            json={
                "username": "admin",
                "password": "password2",
            },
        )

        # Check the response is correct
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_set_admin(empty_postgres_client):
    """
    Test the set_admin endpoint correctly sets an admin user when a
    there's no user yet, or when a valid JWT is provided. Check that
    all other requests are rejected.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    # Login with correct credentials
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Set the admin user
        response = await ac.post(
            "/set-admin",
            json={
                "username": "admin",
                "password": "password",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Admin set successfully"}


@pytest.mark.asyncio
async def test_get_admin(valid_token):
    """
    Checks the get_admin endpoint returns the admin page if the user
    has an authenticated token.
    """

    app.dependency_overrides[get_admin_page] = (
        lambda: "<html><body>Admin Page</body></html>"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/get-admin",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    print(response.text)

    assert "<html><body>Admin Page</body></html>" in response.text


@pytest.mark.asyncio
async def test_add_seed_url(valid_token, empty_postgres_client):
    """
    Checks the add_seed_url endpoint correctly adds a seed url to the
    database with a valid token.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Check the url was added to the database
        results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

        assert len(results) == 1
        assert results[0][0] == 1
        assert results[0][1] == "https://example.com"


@pytest.mark.asyncio
async def test_add_seed_url_without_valid_token(empty_postgres_client):
    """
    Checks the add_seed_url endpoint correctly rejects a request with
    an invalid token.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer this_is_some_invalid_token"},
            json={"url": "https://example.com"},
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}

        # Check the url was added to the database
        results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_delete_seed_url(valid_token, empty_postgres_client):
    """
    Checks the delete_seed_url endpoint correctly deletes a seed url
    from the database with a valid token.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add a seed url to the database
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        response = await ac.post(
            "/delete-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": "https://example.com"},
        )

        # Check the url was deleted from the database
        results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_update_seed_url(valid_token, empty_postgres_client):
    """
    Check that the update_seed_url endpoint correctly updates a seed
    url in the database when a valid token is provided.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add a seed url to the database
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Update the seed url
        response = await ac.post(
            "/update-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "url": "https://snowchild.com",
                "old_url": "https://example.com",
            },
        )

        # Check the url was updated in the database
        results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

        assert len(results) == 1
        assert results[0][0] == 1
        assert results[0][1] == "https://snowchild.com"


@pytest.mark.asyncio
async def test_update_seed_url_invalid_token(
    valid_token,
    empty_postgres_client,
):
    """
    Check that the update_seed_url endpoint refused to update a seed
    url in a database with an invalid token.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add a seed url to the database
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Update the seed url
        response = await ac.post(
            "/update-seed-url",
            headers={"Authorization": f"Bearer jaslkdfjalksdjf"},
            json={
                "url": "https://snowchild.com",
                "old_url": "https://example.com",
            },
        )

        # Check the url was updated in the database
        results = await empty_postgres_client.fetch("SELECT * FROM seed_urls")

        assert len(results) == 1
        assert results[0][0] == 1
        assert results[0][1] == "https://example.com"


@pytest.mark.asyncio
async def test_get_seed_urls(valid_token, empty_postgres_client):
    """
    Check that the get_seed_urls endpoint correctly returns a list of
    seed urls from the database.
    """

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # List of urls to add to the database
        urls_to_add = [
            "https://example.com",
            "https://snowchild.com",
            "https://casey.com",
        ]

        # Add the seed urls to the database
        for url in urls_to_add:
            response = await ac.post(
                "/add-seed-url",
                headers={"Authorization": f"Bearer {valid_token}"},
                json={"url": url},
            )

            assert response.status_code == 200
            assert response.json() == {"message": "Seed url added successfully"}

        # Get the seed urls
        response = await ac.get(
            "/get-seed-urls",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Check the reponse is okay
        assert response.status_code == 200

        # Turn the urls into the expected JSON format
        url_json = [{"url": url} for url in urls_to_add]

        # Check the response has the correct information
        assert response.json() == url_json


@pytest.mark.asyncio
async def test_get_crawled_urls(
    valid_token,
    populated_postgres_client,
):
    """
    Check that the get-searchable-urls endpoint correctly returns the
    list of all urls that have been crawled.
    """

    # Override the dependency to use the populated postgres client
    app.dependency_overrides[get_postgres_client] = (
        lambda: populated_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Get the searchable urls
        response = await ac.get(
            "/get-crawled-urls",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Check the reponse is okay
        assert response.status_code == 200

        # Check the response has the correct information
        crawled_urls = response.json()

        # Check the response has the correct information
        assert len(crawled_urls) == 1
        assert crawled_urls[0]["url"] == "https://caseyhandmer.wordpress.com/"
        assert crawled_urls[0]["firstVisited"] is not None
        assert (
            datetime.strptime(
                crawled_urls[0]["firstVisited"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            < datetime.now()
        )
        assert crawled_urls[0]["lastVisited"] is not None
        assert (
            datetime.strptime(
                crawled_urls[0]["lastVisited"], "%Y-%m-%dT%H:%M:%S.%f"
            )
            < datetime.now()
        )
        assert crawled_urls[0]["allVisits"] == 1
        assert crawled_urls[0]["externalLinks"] == []


@pytest.mark.asyncio
async def test_get_potential_urls(
    valid_token,
    empty_postgres_client,
):
    """
    Checks the get_potential_urls endpoint correctly returns a list of
    potential urls from the database.
    """

    dummy_potential_url = (
        "https://snowchild.com",
        datetime.now(),
        1,
    )

    query = "INSERT INTO potential_urls (url, firstSeen, timesSeen) VALUES ($1, $2, $3)"

    await empty_postgres_client.execute(query, *dummy_potential_url)

    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Get the potential urls
        response = await ac.get(
            "/get-potential-urls",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Check the reponse is okay
        assert response.status_code == 200

        # Check the response has the correct information
        potential_urls = response.json()

        # Check the response has the correct information
        assert len(potential_urls) == 1
        assert potential_urls[0]["url"] == "https://snowchild.com"
        assert potential_urls[0]["firstSeen"] is not None
        assert potential_urls[0]["timesSeen"] == 1


@pytest.mark.asyncio
async def test_start_crawl(
    valid_token,
    empty_postgres_client,
    vector_client,
    local_site,
):
    """
    Checks the start_crawl endpoint correctly starts a crawl and
    searches a webpage.
    """

    # Override fastapi dependency to use test postgres client
    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    # Override fastapi dependency to use test vector client
    app.dependency_overrides[get_qdrant_client] = lambda: vector_client

    # Get the local site url to crawl
    server_url = local_site + "/page1.html"

    print(server_url)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add the test url to the seed urls
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": server_url},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Start a crawl
        response = await ac.post(
            "/start-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "regex": ["https://", "http://"],
                "max_iter": 4,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Crawl started successfully",
            "streamToken": None,
        }

        await asyncio.sleep(5)

        # Stop the crawl
        response = await ac.post(
            "/stop-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

    # Check the vectors and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings",
        with_payload=True,
        with_vectors=True,
    )

    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )

    points = points[0]

    assert len(points) == 4

    # Check the database has the correct number of resources
    results = await empty_postgres_client.fetch("SELECT * FROM resources")
    assert len(results) == 4

    # Check the set of urls stored is the same
    vector_urls = [p.payload["text"]["url"] for p in points]
    db_urls = [r[1] for r in results]
    assert set(vector_urls) == set(db_urls)

    # Check the links and the urls are correct
    assert results[0][1] == server_url
    assert results[0][5][0] == f"{local_site}/page2.html"

    assert results[1][1] == f"{local_site}/page2.html"
    assert results[1][5][0] == f"{local_site}/page1.html"


@pytest.mark.asyncio
async def test_stop_crawl(
    valid_token,
    empty_postgres_client,
    vector_client,
    local_site,
):
    """
    Test the stop_crawl endpoint correctly stops a crawl.
    """

    # Override fastapi dependency to use test postgres client
    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    # Override fastapi dependency to use test vector client
    app.dependency_overrides[get_qdrant_client] = lambda: vector_client

    # Get the local site url to crawl
    server_url = local_site + "/page1.html"

    print(server_url)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add the test url to the seed urls
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": server_url},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Start a crawl
        response = await ac.post(
            "/start-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "regex": ["https://", "http://"],
                "max_iter": 4,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Crawl started successfully",
            "streamToken": None,
        }

        # Stop the crawl
        response = await ac.post(
            "/stop-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"streamToken": None},
        )

        await asyncio.sleep(1)

        assert response.status_code == 200
        assert response.json() == {"message": "Crawl stopped successfully"}

    # Check the vectors and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings",
        with_payload=True,
        with_vectors=True,
    )

    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )

    points = points[0]

    print("Vectors stored:", len(points))

    assert len(points) < 4

    # Check the database has the correct number of resources
    results = await empty_postgres_client.fetch("SELECT * FROM resources")

    print("Result length:", len(results))

    assert len(results) < 4


@pytest.mark.asyncio
async def test_toggle_crawl(
    valid_token,
    empty_postgres_client,
    vector_client,
    local_site,
):
    """
    Test the pause_crawl endpoint correctly pauses a crawl.
    """

    # Override fastapi dependency to use test postgres client
    app.dependency_overrides[get_postgres_client] = (
        lambda: empty_postgres_client
    )

    # Override fastapi dependency to use test vector client
    app.dependency_overrides[get_qdrant_client] = lambda: vector_client

    # Get the local site url to crawl
    server_url = local_site + "/page1.html"

    print(server_url)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Add the test url to the seed urls
        response = await ac.post(
            "/add-seed-url",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"url": server_url},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Seed url added successfully"}

        # Start a crawl
        response = await ac.post(
            "/start-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "regex": ["https://", "http://"],
                "max_iter": 4,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Crawl started successfully",
            "streamToken": None,
        }

        # Pause the crawl
        response = await ac.post(
            "/toggle-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        await asyncio.sleep(1)

        assert response.status_code == 200
        assert response.json() == {"message": "Crawl toggled successfully"}

        # Check the vectors and metadata were stored correctly
        points = await vector_client.scroll(
            collection_name="embeddings",
            with_payload=True,
            with_vectors=True,
        )

        points = await vector_client.scroll(
            collection_name="embeddings", with_payload=True, with_vectors=True
        )

        points = points[0]

        assert len(points) < 4

        # Check the database has the correct number of resources
        results = await empty_postgres_client.fetch("SELECT * FROM resources")

        assert len(results) < 4

        # Restart the crawl
        response = await ac.post(
            "/toggle-crawl",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Crawl toggled successfully"}

        await asyncio.sleep(50)

    # Check the vectors and metadata were stored correctly
    points = await vector_client.scroll(
        collection_name="embeddings",
        with_payload=True,
        with_vectors=True,
    )

    points = await vector_client.scroll(
        collection_name="embeddings", with_payload=True, with_vectors=True
    )

    points = points[0]

    assert len(points) == 4

    # Check the database has the correct number of resources
    results = await empty_postgres_client.fetch("SELECT * FROM resources")
    assert len(results) == 4

    # Check the set of urls stored is the same
    vector_urls = [p.payload["text"]["url"] for p in points]
    db_urls = [r[1] for r in results]
    assert set(vector_urls) == set(db_urls)

    # Check the links and the urls are correct
    assert results[0][1] == server_url
    assert results[0][5][0] == f"{local_site}/page2.html"

    assert results[1][1] == f"{local_site}/page2.html"
    assert results[1][5][0] == f"{local_site}/page1.html"
