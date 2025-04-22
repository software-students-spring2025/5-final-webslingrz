import pytest
import sys
import os

# Ensure the parent directory is on sys.path for importing app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirect
    assert '/dashboard' in response.headers['Location']

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_page_loads(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b"Login" in response.data

def test_birds_requires_login(client):
    response = client.get('/birds', follow_redirects=True)
    assert b"Login" in response.data

def test_play_requires_login(client):
    response = client.get('/play', follow_redirects=True)
    assert b"Login" in response.data

def test_build_game_requires_login(client):
    response = client.post('/build-game')
    assert response.status_code == 401
    assert b"Not logged in" in response.data
