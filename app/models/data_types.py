from pydantic import BaseModel
from datetime import datetime


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
    type: str


class CrawlToken(BaseModel):
    token: str


class SeedUrl(BaseModel):
    url: str


class CrawledUrl(BaseModel):
    url: str
    firstVisited: datetime
    lastVisited: datetime
    allVisits: int
    externalLinks: list[str]

class UrlUpdateData(BaseModel):
    url: str
