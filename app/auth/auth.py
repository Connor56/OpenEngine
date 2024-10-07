"""
Description:
    Authentication functions for the FastAPI application.

Created:
    2024-10-05
"""

import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import asyncpg
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv(dotenv_path="../../.env")

# Secret key and algorithm used to encode/decode JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def set_credentials(
    username: str,
    password: str,
    postgres_client: asyncpg.Connection,
    token: Optional[str] = None,
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

    token : Optional[str], optional
        A token to authenticate the requester is the admin user. If
        this is not provided, the function will only set admin
        credentials if the admins table is empty.

    Returns
    -------
    bool
        True if the credentials were set correctly, False otherwise.
    """
    if token is None:
        # Check if the admins table is empty
        query = "SELECT count(*) FROM admins;"
        result = await postgres_client.fetchrow(query)

        if result[0] > 0:
            print("No JWT provided and admins table is not empty")
            return False

    else:
        # Check if the JWT is valid
        if not check_access_token(token):
            print("JWT is invalid")
            return False

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


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates a JWT token with the users information.

    Parameters
    ----------
    data : dict
        The data to encode in the token.

    expires_delta : Optional[timedelta], optional
        The expiration time for the token, by default None.

    Returns
    -------
    str
        The JWT as a string.
    """
    # Data to encode in the token
    to_encode = data.copy()

    # Get the current time in UTC
    utc_time = datetime.now(timezone.utc)

    # Set the expiration date for the token
    if expires_delta:
        expire = utc_time + expires_delta
    else:
        expire = utc_time + timedelta(minutes=30)

    # Add to the encode dictionary
    to_encode |= {"exp": expire}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def check_access_token(token: str) -> bool:
    """
    Checks if the access token is valid.

    Parameters
    ----------
    token : str
        The access token to check.

    Returns
    -------
    bool
        True if the token is valid, False otherwise.
    """
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print("Token is valid")

        return True

    except jwt.exceptions.InvalidSignatureError:
        print("Token is invalid signature")

        return False

    except jwt.exceptions.ExpiredSignatureError:
        print("Token has expired")

        return False
