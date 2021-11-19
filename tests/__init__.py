import typing as tp

from fastapi.testclient import TestClient
from app import api
import random


TEST_USER = {"username": "...", "password": "..."}
FAKE_USER = {"username": "".join(chr(_) for _ in [random.randint(65, 90) for _ in range(10)]), "password": "123456789"}


client = TestClient(api)


def login(fake: bool = False) -> str:
    """Get jwt token"""
    if fake:
        token = client.post("/token", data=FAKE_USER)
    else:
        token = client.post("/token", data=TEST_USER)
    return token.json().get("access_token", None)
