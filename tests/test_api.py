import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_reports_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_add_item_returns_id(client):
    r = client.post("/items", json={"name": "widget", "quantity": 5})
    assert r.status_code == 201
    assert isinstance(r.get_json()["id"], int)


def test_added_item_is_listed(client):
    client.post("/items", json={"name": "gadget", "quantity": 3})
    items = client.get("/items").get_json()
    assert any(i["name"] == "gadget" and i["quantity"] == 3 for i in items)


def test_quantity_defaults_to_zero(client):
    client.post("/items", json={"name": "bolt"})
    items = client.get("/items").get_json()
    assert any(i["name"] == "bolt" and i["quantity"] == 0 for i in items)
