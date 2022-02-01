from fastapi.testclient import TestClient
from app import api
import random
import os

# TO RUN TESTS SET ENVVARS ANALYTICS_TEST_ADMIN_USERNAME AND ANALYTICS_TEST_ADMIN_PASSWORD
TEST_USER = {
    "username": os.environ.get("ANALYTICS_TEST_ADMIN_USERNAME"),
    "password": os.environ.get("ANALYTICS_TEST_ADMIN_PASSWORD"),
}
FAKE_USER = {"username": "".join(chr(_) for _ in [random.randint(65, 90) for _ in range(10)]), "password": "123456789"}


client = TestClient(api)


def login(fake: bool = False) -> str:
    """Get jwt token"""
    if fake:
        token = client.post("/token", data=FAKE_USER)
    else:
        token = client.post("/token", data=TEST_USER)
    return token.json().get("access_token", None)
