import pytest
from flask import session
from werkzeug.security import generate_password_hash
from backend.app import app
import backend.app as app_module
import backend.game as game_module
# import backend.auth as auth_module
from unittest.mock import MagicMock

# # ---------------------- Fixtures ----------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def authed_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = "mock_user_id"
    return client

# ---------------------- App.py Tests ----------------------

def test_home_redirect(client):
    res = client.get("/")
    assert res.status_code == 302
    assert '/dashboard' in res.headers['Location']

# # ---------------------- Auth.py Tests ----------------------

def test_register_flow(client, monkeypatch):
    fake_users = {}

    class DummyUsers:
        def find_one(self, query): 
            return fake_users.get(query.get("username"))
        def insert_one(self, doc): 
            fake_users[doc["username"]] = doc

    dummy_mongo = type("Mongo", (), {"db": type("DB", (), {"users": DummyUsers()})})()

    monkeypatch.setattr(app_module, "get_mongo", lambda: dummy_mongo)
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Bird Game" in response.data

def test_login_flow(client, monkeypatch):
    fake_users = {}

    class DummyUsers:
        def find_one(self, query): return fake_users.get(query.get("username"))
        def insert_one(self, doc): fake_users[doc["username"]] = doc

    dummy_mongo = type("Mongo", (), {"db": type("DB", (), {"users": DummyUsers()})})()
    monkeypatch.setattr(app_module, "get_mongo", lambda: dummy_mongo)
    
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123'
    })

    assert response.status_code == 302

    response = client.post('/login', data={
        'username': 'newuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Bird Game" in response.data

# def test_register_and_login_flow(client, monkeypatch):
#     fake_users = {}

#     class DummyUsers:
#         def find_one(self, query): return fake_users.get(query.get("username"))
#         def insert_one(self, doc): fake_users[doc["username"]] = doc

#     dummy_mongo = type("Mongo", (), {"db": type("DB", (), {"users": DummyUsers()})})()
#     monkeypatch.setattr(app_module, "get_mongo", lambda: dummy_mongo)
#     # monkeypatch.setattr(app_module.login.__globals__, "get_mongo", lambda: dummy_mongo)

#     # Register new
#     res = client.post("/register", data={"username": "testuser", "password": "secret"}, follow_redirects=True)
#     assert b"Bird Game" in res.data

#     # Register again
#     res = client.post("/register", data={"username": "testuser", "password": "secret"}, follow_redirects=True)
#     assert b"Username already exists" in res.data

#     # Invalid login
#     res = client.post("/login", data={"username": "wrong", "password": "bad"}, follow_redirects=True)
#     assert b"Invalid credentials" in res.data

#     # Valid login
#     fake_users["testuser"]["password"] = generate_password_hash("secret")
#     res = client.post("/login", data={"username": "testuser", "password": "secret"}, follow_redirects=True)
#     assert b"Dashboard" in res.data

# def test_birds_authed(authed_client, monkeypatch):
#     monkeypatch.setattr(game_module, "get_mongo", lambda: type("MockMongo", (), {
#         "db": type("DB", (), {"users": type("Users", (), {
#             "find_one": lambda self, q: {"birds": [{"name": "Duckling", "rarity": "common", "gold_per_minute": 0.6}]}
#         })()})
#     })())
#     res = authed_client.get("/birds")
#     assert b"Duckling" in res.data

def test_update_birds(client):
    # Unauthorized
    res = client.post("/update-birds", json={"birds": []})
    assert res.status_code == 401

def test_update_money(client):
    # Unauthorized
    res = client.post("/update-money", json={"money": 100})
    assert res.status_code == 401

# def test_dashboard_authed(authed_client, monkeypatch):
#     monkeypatch.setattr(game_module, "get_mongo", lambda: type("MockMongo", (), {
#         "db": type("DB", (), {"users": type("Users", (), {
#             "find_one": lambda self, q: {"money": 50}
#         })()})
#     })())
#     res = authed_client.get("/dashboard")
#     assert b"$50" in res.data or res.status_code == 200

# def test_birds_authed(authed_client, monkeypatch):
#     monkeypatch.setattr(game_module, "get_mongo", lambda: type("MockMongo", (), {
#         "db": type("DB", (), {"users": type("Users", (), {
#             "find_one": lambda self, q: {"birds": [{"name": "Duckling", "rarity": "common", "gold_per_minute": 0.6}]}
#         })()})
#     })())
#     res = authed_client.get("/birds")
#     assert b"Duckling" in res.data

def test_update_birds(client):
    # Unauthorized
    res = client.post("/update-birds", json={"birds": []})
    assert res.status_code == 401

# def test_update_money(client):
#     # Unauthorized
#     res = client.post("/update-money", json={"money": 100})
#     assert res.status_code == 401

#     # Invalid
#     with client.session_transaction() as sess:
#         sess['user_id'] = "mock"
#     res = client.post("/update-money", json={})
#     assert res.status_code == 400

#     # Valid
#     monkeypatch = pytest.MonkeyPatch()
#     monkeypatch.setattr(game_module, "get_mongo", lambda: type("MockMongo", (), {
#         "db": type("DB", (), {
#             "users": type("Users", (), {"update_one": lambda *a, **kw: None})()
#         })
#     })())
#     res = client.post("/update-money", json={"money": 50})
#     assert res.json["success"]

# def test_update_birds(client):
#     # Unauthorized
#     res = client.post("/update-birds", json={"birds": []})
#     assert res.status_code == 401

#     # Invalid
#     with client.session_transaction() as sess:
#         sess['user_id'] = "mock"
#     res = client.post("/update-birds", json={})
#     assert res.status_code == 400

#     # Valid
#     monkeypatch = pytest.MonkeyPatch()
#     monkeypatch.setattr(game_module, "get_mongo", lambda: type("MockMongo", (), {
#         "db": type("DB", (), {
#             "users": type("Users", (), {"update_one": lambda *a, **kw: None})()
#         })
#     })())
#     res = client.post("/update-birds", json={"birds": [{"name": "Duckling"}]})
#     assert res.json["success"]

# ---------------------- Utilities ----------------------

def test_load_scaled_image(monkeypatch):
    import bird_game.main
    class DummyImg:
        def get_height(self): return 100
        def get_width(self): return 100
    monkeypatch.setattr("pygame.image.load", lambda p: DummyImg())
    monkeypatch.setattr("pygame.transform.scale", lambda img, size: "scaled")
    result = bird_game.main.load_scaled_image("fakepath", 50)
    assert result == "scaled"

def test_greyscale_surface():
    import pygame
    import bird_game.main
    surface = pygame.Surface((10, 10))
    surface.fill((255, 255, 255))
    grey = bird_game.main.greyscale_surface(surface)
    assert isinstance(grey, pygame.Surface)
