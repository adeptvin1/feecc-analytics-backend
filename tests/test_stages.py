from datetime import datetime
from . import client, login


def test_get_stages_unauthorized():
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/stages/")
    assert r.status_code != 200, "unattended access"


def test_get_stages_authorized():
    token = login()
    r = client.get("/api/v1/stages/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_get_stages_with_decoded_employees_authorized():
    token = login()
    r = client.get("/api/v1/stages/?decode_employees=true", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_create_stage():
    stage = {
        "name": "testing",
        "employee_name": None,
        "parent_unit_uuid": "123456",
        "session_start_time": str(datetime.now()),
        "session_end_time": str(datetime.now()),
        "video_hashes": None,
        "additional_info": {},
        "id": "123456",
        "is_in_db": False,
        "creation_time": str(datetime.now()),
    }
    token = login()
    r = client.post("/api/v1/stages/", headers={"Authorization": f"Bearer {token}"}, json=stage)
    assert r.status_code == 200, r.json()


def test_check_new_stage():
    token = login()
    r = client.get("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("stage", None) is not None, r.json()
    assert r.json().get("stage", None)["name"] == "testing"


def test_remove_created_stage():
    token = login()
    r = client.delete("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200
