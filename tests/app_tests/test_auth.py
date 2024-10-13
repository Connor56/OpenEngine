import pytest

import app.auth.auth as auth
from argon2 import PasswordHasher
import asyncpg
import jwt
from datetime import timedelta, datetime


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
        token="test_jwt",
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


def test_create_access_token():
    """
    Check if the create_access_token function correctly creates a
    JWT token with the correct data.
    """

    # Create a dictionary to use as the data
    data = {"username": "admin", "password": "password"}

    # Create the token
    token = auth.create_access_token(data)

    # Decode the token
    decoded_token = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])

    # Check if the token is valid
    assert decoded_token["username"] == data["username"]
    assert decoded_token["password"] == data["password"]


def test_check_access_token():
    """
    Check if the check_access_token function correctly checks if a
    token is valid.
    """

    # Create a dictionary to use as the data
    data = {"username": "admin"}

    # Create the token
    token = auth.create_access_token(data)

    # Check if the token is valid
    assert auth.check_access_token(token)

    # Check the token fails if its invalid
    assert not auth.check_access_token(token + "1234")

    assert not auth.check_access_token("something")

    # Create a new token that's expired
    data = {"username": "admin2"}
    token = auth.create_access_token(
        data,
        expires_delta=timedelta(minutes=-5),
    )

    # Check if the token is valid
    assert not auth.check_access_token(token)
