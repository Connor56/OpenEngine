"""
Description:
    Authentication functions for the FastAPI application.

Created:
    2024-10-05
"""

from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncpg
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv(dotenv_path="../../.env")


async def set_credentials(
    username: str,
    password: str,
    postgres_client: asyncpg.Connection,
) -> bool:
    """
    Sets credentials for an admin user in the admins table.

    Parameters
    ----------
    username : str
        The username of the admin user.

    password : str
        The password of the admin user.

    postgres_client : asyncpg.Connection
        The PostgreSQL client.

    Returns
    -------
    bool
        True if the credentials were set correctly, False otherwise.
    """
    # Hash the password
    password_hash = PasswordHasher().hash(password)

    # Insert the credentials into the database
    query = "INSERT INTO admins (username, password) VALUES ($1, $2)"
    try:
        await postgres_client.execute(query, username, password_hash, timeout=5)
    except Exception as e:
        print("Couldn't set credentials:", e)
        return False

    return True


async def check_credentials(
    username: str,
    password: str,
    postgres_client: asyncpg.Connection,
) -> bool:
    """
    Checks the credentials of a user.

    Parameters
    ----------
    username : str
        The username of the user.

    password : str
        The password of the user.

    postgres_client : asyncpg.Connection
        The PostgreSQL client.

    Returns
    -------
    bool
        True if the credentials are valid, False otherwise.
    """
    # Check if the user exists in the database
    query = "SELECT * FROM admins WHERE username = $1"
    result = await postgres_client.fetchrow(query, username)

    # If the user doesn't exist, return false
    if result is None:
        print("User doesn't exist")
        return False

    # Check if the password is correct
    try:
        PasswordHasher().verify(result["password"], password)
        print("Password is correct")
        return True

    except VerifyMismatchError:
        print("Password is incorrect")
        return False
