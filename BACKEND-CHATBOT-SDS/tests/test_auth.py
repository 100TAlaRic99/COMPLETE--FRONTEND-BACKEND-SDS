def test_register_requires_fields(client):
    res = client.post("/api/register", json={"username": "u"})
    assert res.status_code == 400


def test_register_success(client):
    res = client.post(
        "/api/register",
        json={"username": "alice", "email": "a@example.com", "password": "pw"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert "access_token" in body
    assert body["user"]["email"] == "a@example.com"


def test_register_rejects_duplicate_email(client):
    client.post(
        "/api/register",
        json={"username": "alice", "email": "a@example.com", "password": "pw"},
    )
    res = client.post(
        "/api/register",
        json={"username": "bob", "email": "a@example.com", "password": "pw"},
    )
    assert res.status_code == 409


def test_login_requires_fields(client):
    res = client.post("/api/login", json={"email": "a@example.com"})
    assert res.status_code == 400


def test_login_rejects_invalid_credentials(client):
    res = client.post("/api/login", json={"email": "nope@example.com", "password": "pw"})
    assert res.status_code == 401


def test_login_success(client):
    client.post(
        "/api/register",
        json={"username": "alice", "email": "a@example.com", "password": "pw"},
    )
    res = client.post("/api/login", json={"email": "a@example.com", "password": "pw"})
    assert res.status_code == 200
    body = res.get_json()
    assert "access_token" in body
    assert body["user"]["username"] == "alice"

