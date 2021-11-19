from . import client, login


def test_get_passports_unauthorized():
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/passports/")
    assert r.status_code != 200, "unattended access"


def test_get_passports_authorized():
    token = login()
    r = client.get("/api/v1/passports/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_create_passport():
    passport = {
        "uuid": "123456",
        "internal_id": "123456",
        "passport_short_url": "url",
        "is_in_db": False,
        "biography": None,
        "components_units": {},
        "featured_in_int_id": "123456",
        "barcode": None,
        "model": "testing",
    }
    token = login()
    r = client.post("/api/v1/passports/", headers={"Authorization": f"Bearer {token}"}, json=passport)
    assert r.status_code == 200, r.json()


def test_check_new_passport():
    token = login()
    r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("passport", None) is not None, r.json()
    assert r.json().get("passport", None)["model"] == "testing"


def test_remove_created_passport():
    token = login()
    r = client.delete("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200


def test_check_deleted_passport():
    token = login()
    r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("passport", None) is None, r.json()
