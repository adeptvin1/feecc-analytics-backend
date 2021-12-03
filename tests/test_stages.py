from datetime import datetime

import pytest

from . import client, login


def test_get_stages_unauthorized():
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/stages/")
    assert r.status_code != 200, "unattended access"


def test_get_stages_authorized():
    token = login()
    r = client.get("/api/v1/stages/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


@pytest.mark.slow
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


def test_patch_stage():
    token = login()
    stage_patch = {
        "name": "patched",
        "employee_name": "tester",
        "parent_unit_uuid": "fake",
        "session_start_time": str(datetime.now()),
        "session_end_time": str(datetime.now()),
        "video_hashes": ["hash1", "hash2", "hash3"],
        "additional_info": {"patched": True},
        "id": "fakeid",
        "is_in_db": True,
        "creation_time": str(datetime.now()),
    }
    r = client.patch("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"}, json=stage_patch)
    assert r.json().get("status_code") == 200, r.json()


def test_get_patched_stage():
    """
    You're now unable to edit such fields as:
    "parent_unit_uuid","session_start_time","session_end_time","id","is_in_db","creation_time"
    """
    token = login()
    r = client.get("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["status_code"] == 200, r.json()
    assert r.json().get("stage", None) is not None, r.json()
    assert r.json().get("stage").get("name") == "patched", f"Failed to patch name. Resp: {r.json()}"
    assert r.json().get("stage").get("employee_name") == "tester", f"Failed to patch employee_name. Resp: {r.json()}"
    assert r.json().get("stage").get("additional_info")["patched"], f"Failed to patch additional_info. Resp: {r.json()}"
    assert len(r.json().get("stage").get("video_hashes")) == 3, f"Failed to patch video_hashes. Resp: {r.json()}"

    assert r.json().get("stage").get("id") != "fakeid", f"Patched immutable field. Resp: {r.json()}"
    assert not r.json().get("stage").get("is_in_db"), f"Patched immutable field. Resp: {r.json()}"


def test_remove_created_stage():
    token = login()
    r = client.delete("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200


def test_check_removed_stage():
    token = login()
    r = client.get("/api/v1/stages/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("stage", None) is None, f"expected None got {r.json()}"


def test_check_nonexistent_stage():
    token = login()
    r = client.get("/api/v1/stages/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("stage", None) is None, f"expected None got {r.json()}"
    assert r.json().get("status_code", None) == 404, r.json()
