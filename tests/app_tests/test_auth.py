import pytest

import app.auth.auth as auth
from argon2 import PasswordHasher
import asyncpg


@pytest.mark.asyncio
async def test_set_credentials(
    empty_postgres_client: asyncpg.Connection,
):
    """
    Check if the set_credentials function correctly sets the
    credentials of an admin user.
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
