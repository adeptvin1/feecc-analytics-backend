import typing as tp

from fastapi import HTTPException, status
from loguru import logger
from starlette.status import HTTP_408_REQUEST_TIMEOUT


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


class ConnectionTimeoutException(HTTPException):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_408_REQUEST_TIMEOUT
        self.detail = "Timeout"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class IncorrectAddressException(HTTPException):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Can't parse given address. It must starts with http(s)://"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")


class ParserException(HTTPException):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = "Can't parse given document. Looks like it's not YAML-like"
        self.headers = {"WWW-Authenticate": "Bearer"}

        logger.warning(f"{self.detail} : {kwargs}")
