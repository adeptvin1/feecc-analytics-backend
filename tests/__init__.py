from fastapi.testclient import TestClient
from app import api


TEST_USER = {"username": "...", "password": "..."}


client = TestClient(api)


def login() -> str:
    """Get jwt token"""
    token = client.post("/token", data=TEST_USER)
    return token.json().get("access_token", None)
