"""
Description:
    The FastAPI application for the OpenEngine project.

Created:
    2024-09-29
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Optional
import app.auth.auth as auth
from app.models.data_types import LoginData, Token, CrawlToken, SeedUrl, UrlUpdateData
from dotenv import load_dotenv
import asyncpg
from qdrant_client import AsyncQdrantClient
import os
import app.core.storage as storage
from fastapi.responses import HTMLResponse

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


async def check_token(token: str = Depends(oauth2_scheme)):
    """
    Checks that the token is valid and returns the user's username.
    """
    return auth.check_access_token(token)


@app.post("/login", response_model=Token)
async def admin_login(
    login_data: LoginData,
    postgres_client=Depends(get_postgres_client),
):
    """
    Logs in an admin user by checking their credentials and returning
    a JWT if the user is allowed access to the admin panel.
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


@app.post("/set-admin")
async def set_admin(
    request: Request,
    postgres_client=Depends(get_postgres_client),
):
    """
    Sets the credentials of an admin user if they have a valid JWT or
    if no admin user has been set yet.
    """
    # Get the authorisation header
    auth_header = request.headers.get("Authorization")

    # Get the token if it exists
    token = None

    if auth_header is not None:
        token = auth_header.split(" ")[1]

    # Get the admin data
    json = await request.json()
    admin_data = LoginData(**json)

    # Attempt to set the admin data
    was_set = await auth.set_credentials(
        admin_data.username,
        admin_data.password,
        postgres_client,
        token=token,
    )

    if was_set:
        return {"message": "Admin set successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't set admin",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_admin_page():
    """
    Loads and returns the static admin page as html text.
    """
    return "placeholder"


@app.get("/get-admin")
async def get_admin(
    token: str = Depends(oauth2_scheme),
    page: str = Depends(get_admin_page),
):
    """
    Get the admin frontend for the user to work with and make admin
    changes to the backend of the site.
    """
    if not auth.check_access_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return HTMLResponse(content=page)


@app.post("/add-seed-url")
async def add_seed_url(
    url: SeedUrl,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Add a new url to the seed urls table in the database.
    """
    if not auth.check_access_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Add the url to the database
    await storage.add_seed_url(url.url, postgres_client)
    return {"message": "Seed url added successfully"}


@app.post("/delete-seed-url")
async def delete_seed_url(
    url: SeedUrl,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Delete a url from the seed urls table in the database.
    """
    if not auth.check_access_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Delete the url from the database
    await storage.delete_seed_url(url.url, postgres_client)


@app.post("/update-seed-url")
async def update_seed_url(
    url: UrlUpdateData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Update an url in the seed urls table in the database.
    """
    pass


@app.post("/start-crawl", response_model=CrawlToken)
async def start_crawl(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
    qdrant_client=Depends(get_qdrant_client),
):
    """
    Start the url crawling process.
    """
    pass


@app.post("/stop-crawl")
async def stop_crawl(
    crawl_token: CrawlToken,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Uses a crawl token to find the crawling process and stop it.
    """
    pass


@app.post("/pause-crawl")
async def pause_crawl(
    crawl_token: CrawlToken,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Uses a crawl token to find the crawling process and pause it.
    """
    pass


@app.get("/get-seed-urls", response_model=list[SeedUrl])
async def get_seed_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get the seed urls from the database.
    """
    pass


@app.get("/get-searchable-urls", response_model=list[SeedUrl])
async def get_searchable_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get all the searchable urls from the database. These are the urls
    that have been crawled and processed.
    """
    pass


@app.get("/get-potential-urls", response_model=list[SeedUrl])
async def get_potential_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get all the potential urls from the database. These are the urls
    that have been seen during crawls but discarded because they
    didn't pass the filter algorithms.
    """
    pass
