import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app, get_postgres_client, get_admin_page
from app.auth.auth import set_credentials
from fastapi.responses import JSONResponse


@pytest.mark.asyncio
async def test_login(empty_postgres_client):
    """
    Test the login endpoint correctly authenticates an admin user, returns
    a valid token, but reject an invalid user.
    """

    # Add an admin user to the postgres database
    assert await set_credentials("admin", "password", empty_postgres_client)

    app.dependency_overrides[get_postgres_client] = lambda: empty_postgres_client

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

    app.dependency_overrides[get_postgres_client] = lambda: empty_postgres_client

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

    app.dependency_overrides[get_postgres_client] = lambda: empty_postgres_client

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

    app.dependency_overrides[get_postgres_client] = lambda: empty_postgres_client

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

    app.dependency_overrides[get_postgres_client] = lambda: empty_postgres_client

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
