import pytest

import app.auth.auth as auth
from argon2 import PasswordHasher
import asyncpg
import jwt


@pytest.mark.asyncio
async def test_set_credentials(
    empty_postgres_client: asyncpg.Connection,
):
    """
    Check if the set_credentials function correctly sets the
    credentials of an admin user, and won't set more credentials if
    one already exists and a valid JWT isn't provided with the
    function call.
    """

    # Username and password to use
    password = "password"
    username = "admin"

    # Set the credentials
    await auth.set_credentials(username, password, empty_postgres_client)

    # Check if the credentials were set correctly
    query = "SELECT * FROM admins"
    result = await empty_postgres_client.fetchrow(query)

    password_hash = result["password"]

    # Check if the credentials were set correctly
    assert result is not None
    assert result["username"] == username
    assert PasswordHasher().verify(password_hash, password)

    # Username and password to use
    password = "password2"
    username = "admin2"

    # Attempt to set the credentials
    was_set = await auth.set_credentials(
        username,
        password,
        empty_postgres_client,
    )

    # Check the function says the credentials weren't set
    assert not was_set

    # Check the credentials aren't in postgres
    query = "SELECT * FROM admins"
    result = await empty_postgres_client.fetch(query)

    assert len(result) == 1
    assert result[0]["username"] != username


@pytest.mark.asyncio
async def test_set_credentials_with_jwt(
    empty_postgres_client,
    mocker,
):
    """
    Check if the set_credentials function correctly sets the
    credentials of an admin user when a JWT is provided, despite a
    single admin already existing.
    """

    # Username and password to use
    password = "password"
    username = "admin"

    # Check the credentials are in postgres
    query = "SELECT * FROM admins"
    result = await empty_postgres_client.fetch(query)

    # Set the credentials and assert they are set correctly
    assert await auth.set_credentials(username, password, empty_postgres_client)

    # Check the credentials are in postgres
    query = "SELECT * FROM admins"
    result = await empty_postgres_client.fetch(query)

    assert len(result) == 1
    assert result[0]["username"] == username

    # Create a new password and username
    password = "password2"
    username = "admin2"

    # Mock the check_access_token function
    mocker.patch("app.auth.auth.check_access_token", return_value=True)

    # Set the credentials with a fake JWT
    assert await auth.set_credentials(
        username,
        password,
        empty_postgres_client,
        jwt="test_jwt",
    )

    # Check the credentials are in postgres
    query = "SELECT * FROM admins"
    result = await empty_postgres_client.fetch(query)

    assert len(result) == 2
    assert result[1]["username"] == username


@pytest.mark.asyncio
async def test_check_credentials(
    empty_postgres_client: asyncpg.Connection,
):
    """
    Check if the check_credentials function correctly checks the
    credentials of an admin user.
    """

    # Username and password to use
    password = "password"
    username = "admin"

    # Set the credentials
    await auth.set_credentials(username, password, empty_postgres_client)

    # Credentials should be correct
    assert await auth.check_credentials(
        username,
        password,
        empty_postgres_client,
    )

    # Credentials should be incorrect
    assert not await auth.check_credentials(
        "admin",
        "wrong_password",
        empty_postgres_client,
    )


