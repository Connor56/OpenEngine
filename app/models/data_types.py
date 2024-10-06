from pydantic import BaseModel


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
    type: str
