from . import client, login, TEST_USER, FAKE_USER


def test_get_data_about_unauthorized_user():
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401, r.json()


def test_get_data_about_authorized_user():
    token = login()
    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("user").get("username", None) == TEST_USER.get("username")


def test_get_data_concrete_user():
    token = login()
    r = client.get(f"/api/v1/users/{TEST_USER.get('username')}", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("user").get("username", None) == TEST_USER.get("username")
    assert isinstance(r.json().get("user").get("is_admin", None), bool)


def test_create_new_user():
    token = login()
    r = client.post("/api/v1/users/", headers={"Authorization": f"Bearer {token}"}, json=FAKE_USER)
    assert r.status_code == 200


def test_auth_as_a_new_user():
    token = login(fake=True)
    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("user").get("username", None), r.json()
    assert not r.json().get("user").get("is_admin", None), r.json()


def test_delete_user():
    token = login()
    r = client.delete(f"/api/v1/users/{FAKE_USER.get('username')}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()

    r = client.get(f"/api/v1/users/{FAKE_USER.get('username')}", headers={"Authorization": f"Bearer {token}"})
    r.json().get("user", None) is None, r.json()
