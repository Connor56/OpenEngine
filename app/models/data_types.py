from pydantic import BaseModel


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
    type: str


class CrawlToken(BaseModel):
    token: str


class UrlData(BaseModel):
    url: str


class UrlUpdateData(BaseModel):
    url: str
