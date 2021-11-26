from . import client, login


def test_get_employees_unauthorized():
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/employees/")
    assert r.status_code != 200, "unattended access"


def test_get_employees_authorized():
    token = login()
    r = client.get("/api/v1/employees/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_create_employee():
    employee = {"rfid_card_id": "123", "name": "test", "position": "test"}
    token = login()
    r = client.post("/api/v1/employees/", headers={"Authorization": f"Bearer {token}"}, json=employee)
    assert r.status_code == 200, r.json()


def test_check_new_employee():
    token = login()
    r = client.get("/api/v1/employees/123", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("employee", None) is not None, r.json()
    assert r.json().get("employee", None)["name"] == "test"


def test_remove_created_employee():
    token = login()
    r = client.delete("/api/v1/employees/123", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["status_code"] == 200


def test_check_removed_employee():
    token = login()
    r = client.get("/api/v1/employees/123", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("employee", None) is None, r.json()


def test_get_nonexistent_employee():
    token = login()
    r = client.get("/api/v1/employees/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("employee", None) is None, r.json()
    assert r.json().get("status_code", None) == 404, r.json()
