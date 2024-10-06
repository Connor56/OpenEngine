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

@app.post("/login")
async def admin_login():

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
    """
    Logs in an admin user by checking their credentials.
    """

    # Create an access token if user is authenticated
    access_token = create_access_token(data={})
    return {"access_token": access_token, "token_type": "bearer"}


# Dependency to extract and validate the JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    return username


# Protected route
@app.get("/hello")
async def read_hello(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}!"}
