from . import client, login


def test_availability():
    assert client.get("/api/v1/status").status_code == 200


def test_login() -> str:
    """Get jwt token"""
    token = login()
    assert token is not None, f"Failed to login"
