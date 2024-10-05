"""
Description:
    The FastAPI application for the OpenEngine project.

Created:
    2024-09-29
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Optional
from auth.auth import create_access_token

app = FastAPI()

# OAuth2 scheme setup (even though we're just using JWT, it's needed here)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Mock authentication function (just returns a token for any request)
@app.post("/token")
async def get_token():

    access_token = create_access_token(data={"sub": ""})
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
