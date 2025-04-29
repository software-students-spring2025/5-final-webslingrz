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

def test_play_flow(client, monkeypatch):
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

    response = client.post('/play')

    assert response.status_code == 405

def test_logout_flow(client, monkeypatch):
    fake_users = {}

    class DummyUsers:
        def find_one(self, query): return fake_users.get(query.get("username"))
        def insert_one(self, doc): fake_users[doc["username"]] = doc

    dummy_mongo = type("Mongo", (), {"db": type("DB", (), {"users": DummyUsers()})})()
    monkeypatch.setattr(app_module, "get_mongo", lambda: dummy_mongo)

    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign In" in response.data

import os

def test_serve_game_assets_real_file(client, monkeypatch):
    real_web_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'static')
    real_web_dir = os.path.abspath(real_web_dir)

    monkeypatch.setattr(app_module, "WEB_DIR", real_web_dir)

    response = client.get("/game-assets/space_ad.png")

    with open(os.path.join(real_web_dir, "space_ad.png"), "rb") as f:
        actual_file_data = f.read()

    assert response.status_code == 200
    assert response.data == actual_file_data
    assert response.headers["Content-Type"].startswith("image/") 

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
