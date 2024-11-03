from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
    type: str


class CrawlToken(BaseModel):
    streamToken: str | None
    message: str


class SeedUrl(BaseModel):
    url: str
    seeds: list[str] | None


class UrlDeleteData(BaseModel):
    url: str


class CrawledUrl(BaseModel):
    url: str
    firstVisited: datetime
    lastVisited: datetime
    allVisits: int
    externalLinks: list[str]


class PotentialUrl(BaseModel):
    url: str
    firstSeen: datetime
    timesSeen: int


class UrlUpdateData(BaseModel):
    url: str
    old_url: str


class CrawlData(BaseModel):
    regex: Optional[List[str]]
    max_iter: Optional[int]


class SeedUpdateData(BaseModel):
    url: str
    new_seed: str
    old_seed: str


class SeedAddDeleteData(BaseModel):
    url: str
    seed: str
