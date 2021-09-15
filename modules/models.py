import typing as tp

from pydantic import BaseModel


class User(BaseModel):
    username: str
    hashed_password: str


class TokenData(BaseModel):
    username: tp.Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
