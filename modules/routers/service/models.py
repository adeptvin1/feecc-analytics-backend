import typing as tp

from pydantic import BaseModel


class TokenData(BaseModel):
    username: tp.Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
