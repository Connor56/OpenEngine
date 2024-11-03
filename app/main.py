"""
Description:
    The FastAPI application for the OpenEngine project.

Created:
    2024-09-29
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Optional
import app.auth.auth as auth
from app.models.data_types import (
    LoginData,
    Token,
    CrawlToken,
    SeedUrl,
    UrlUpdateData,
    CrawledUrl,
    PotentialUrl,
    CrawlData,
    SeedUpdateData,
    SeedAddDeleteData,
    UrlDeleteData,
)
from dotenv import load_dotenv
import asyncpg
from qdrant_client import AsyncQdrantClient
import os
import app.core.storage as storage
from fastapi.responses import HTMLResponse
import asyncio
import app.core.gather as gather
import sentence_transformers

# Get the files containing directory
containing_dir = os.path.dirname(__file__)

# Windows fix with their stupid backslash paths
containing_dir = "/".join(containing_dir.split("\\"))

# Get the parent directory
parent_dir = "/".join(containing_dir.split("/")[:-1])

# Get the env file from the parent directory
env_file = parent_dir + "/.env"

# Load the env file variables into the environment
load_dotenv(dotenv_path=env_file)

# OAuth2 scheme setup (even though we're just using JWT, it's needed here)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Global database clients
postgres_client = None
qdrant_client = None

# Global crawl events
crawl_pause = None
crawl_end = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan sets up the database clients for the app. On
    shutdown the clients are closed.
    """
    global postgres_client
    global qdrant_client

    print(os.getenv("POSTGRES_USER"))

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

    yield


# Set up the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Add middleware to allow CORS
# TODO: Probably drop this when in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows requests from any origin (change this in production for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers, including Authorization
)


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


async def get_crawl_pause():
    """
    Gets the crawl pause event after the lifespan has set it up. Makes
    it much simpler to mock the event in tests.
    """
    return crawl_pause


async def get_crawl_end():
    """
    Gets the crawl end event after the lifespan has set it up. Makes
    it much simpler to mock the event in tests.
    """
    global crawl_end
    return crawl_end


async def check_token(token: str = Depends(oauth2_scheme)):
    """
    Checks that the token is valid and returns the user's username.
    """
    return auth.check_access_token(token)


async def get_embedding_model():
    """
    Gets the embedding model after the lifespan has set it up. Makes
    it much simpler to mock the model in tests.
    """
    return sentence_transformers.SentenceTransformer(
        "multi-qa-MiniLM-L6-cos-v1"
    )


def check_auth(token: str):
    """
    Checks the authorisation of a user and raises an error if they
    don't have authorisation. Allows anything through if the site is on
    dev mode.
    """
    # Skip the check when in DEV mode
    if os.getenv("DEV") == "true":
        return

    if not auth.check_access_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
    check_auth(token)

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
    check_auth(token)

    # Add the url to the database
    response = await storage.add_seed_url(url.url, postgres_client)
    if response:
        return {"message": "Seed url added successfully"}
    else:
        return {"message": "Failed to add seed url"}


@app.post("/delete-seed-url")
async def delete_seed_url(
    url: UrlDeleteData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Delete a url from the seed urls table in the database.
    """
    check_auth(token)

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
    check_auth(token)

    # Update the url in the database
    await storage.update_seed_url(url.old_url, url.url, postgres_client)
    return {"message": "Seed url updated successfully"}


@app.post("/update-seed-url-seed")
async def update_seed_url(
    seed_update: SeedUpdateData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Updates a seed that's stored against an url in the database. The seeds are basically
    the initial pages to crawl associated with that url.
    """
    check_auth(token)

    # Update the url in the database
    result = await storage.update_seed_url_seed(
        seed_update.old_seed,
        seed_update.new_seed,
        seed_update.url,
        postgres_client,
    )

    if result[0]:
        return {"message": "Seed updated successfully"}
    else:
        return {"message": result[1]}


@app.post("/add-seed-to-url")
async def add_seed_to_url(
    seed_add: SeedAddDeleteData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Adds a seed to an url in the database.
    """
    check_auth(token)

    # Add the seed to the url in the database
    result = await storage.add_seed_to_url(
        seed_add.seed,
        seed_add.url,
        postgres_client,
    )
    if result:
        return {"message": "Seed added to url successfully"}
    else:
        return {"message": "Failed to add seed to url"}


@app.post("/delete-seed-from-url")
async def delete_seed_from_url(
    seed_delete: SeedAddDeleteData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Adds a seed to an url in the database.
    """
    check_auth(token)

    # Add the seed to the url in the database
    result = await storage.delete_seed_from_url(
        seed_delete.seed,
        seed_delete.url,
        postgres_client,
    )

    return {"message": result[1]}


@app.post("/start-crawl", response_model=CrawlToken)
async def start_crawl(
    crawl_data: CrawlData,
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
    qdrant_client=Depends(get_qdrant_client),
    embedding_model=Depends(get_embedding_model),
):
    """
    Start the url crawling process.
    """
    check_auth(token)

    print("crawl data:", crawl_data)

    # Set up the events for starting and stopping the crawler
    pause = asyncio.Event()
    end = asyncio.Event()

    # Set the global variables for the crawler
    global crawl_pause
    global crawl_end

    crawl_pause = pause
    crawl_end = end

    # Set up the crawler
    asyncio.create_task(
        gather.gather(
            qdrant_client,
            postgres_client,
            embedding_model,
            max_iter=crawl_data.max_iter,
            regex_patterns=crawl_data.regex,
            pause=pause,
            end=end,
        )
    )

    return {"message": "Crawl started successfully", "streamToken": None}


@app.post("/stop-crawl")
async def stop_crawl(
    crawl_end=Depends(get_crawl_end),
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Uses a crawl token to find the crawling process and stop it.
    """
    check_auth(token)

    crawl_end.set()

    return {"message": "Crawl stopped successfully"}


@app.post("/toggle-crawl")
async def toggle_crawl(
    crawl_pause=Depends(get_crawl_pause),
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Toggle's a crawls state, if it's paused it will be resumed,
    if it's running it will be paused. Setting the event works fir
    """
    check_auth(token)

    # Toggle the pause event
    crawl_pause.set()
    return {"message": "Crawl toggled successfully"}


@app.get("/get-seed-urls", response_model=list[SeedUrl])
async def get_seed_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get the seed urls from the database.
    """
    check_auth(token)

    return await storage.get_seed_urls(postgres_client)


@app.get("/get-crawled-urls", response_model=list[CrawledUrl])
async def get_crawled_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get all the crawled urls from the database. These are the urls
    that have been crawled, processed, and stored in a row in
    postgres.
    """
    check_auth(token)

    return await storage.get_crawled_urls(postgres_client)


@app.get("/get-potential-urls", response_model=list[PotentialUrl])
async def get_potential_urls(
    token=Depends(oauth2_scheme),
    postgres_client=Depends(get_postgres_client),
):
    """
    Get all the potential urls from the database. These are the urls
    that have been seen during crawls but discarded because they
    didn't pass the filter algorithms.
    """
    check_auth(token)

    return await storage.get_potential_urls(postgres_client)
