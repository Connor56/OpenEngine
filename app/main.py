"""
Description:
    The FastAPI application for the OpenEngine project.

Created:
    2024-09-29
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Optional
import app.auth.auth as auth
from app.models.data_types import LoginData, Token
from dotenv import load_dotenv
import asyncpg
from qdrant_client import AsyncQdrantClient
import os

load_dotenv(dotenv_path="../.env")

# OAuth2 scheme setup (even though we're just using JWT, it's needed here)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Global database clients
postgres_client = None
qdrant_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan sets up the database clients for the app. On
    shutdown the clients are closed.
    """
    global postgres_client
    global qdrant_client

    # Set up the database clients
    postgres_client = await asyncpg.connect(
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

    # set up the qdrant client
    qdrant_client = AsyncQdrantClient(
        host=os.getenv("QDRANT_URL"),
        port=os.getenv("QDRANT_PORT"),
    )


# Set up the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


async def get_postgres_client():
    """
    Gets the postgres client after the lifespan has set it up. Makes it
    much simpler to mock the client in tests.
    """
    return postgres_client


async def get_qdrant_client():
    """
    Gets the qdrant client after the lifespan has set it up. Makes it
    much simpler to mock the client in tests.
    """
    return qdrant_client


@app.post("/login", response_model=Token)
async def admin_login(
    login_data: LoginData,
    postgres_client=Depends(get_postgres_client),
):
    """
    Logs in an admin user by checking their credentials.
    """

    # Check if the credentials are correct
    creds_ok = await auth.check_credentials(
        login_data.username,
        login_data.password,
        postgres_client,
    )

    if not creds_ok:
        # Raise an HTTP 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create an access token if user is authenticated
    access_token = auth.create_access_token(data={})

    return {"token": access_token, "type": "bearer"}
