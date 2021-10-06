import typing as tp

from fastapi import HTTPException, status
from loguru import logger


class AuthException(HTTPException):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Incorrect username or password"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class CredentialsValidationException(HTTPException):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")
