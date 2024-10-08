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
