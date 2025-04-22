import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the backend dir is on the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import game

@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = "test_secret"
    app.register_blueprint(game.bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_update_money_invalid_data(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "testid"
    response = client.post("/update-money", json={})
    assert response.status_code == 400

def test_update_money_unauthorized(client):
    response = client.post("/update-money", json={"money": 999})
    assert response.status_code == 401

def test_update_birds_invalid_data(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "testid"
    response = client.post("/update-birds", json={})
    assert response.status_code == 400

def test_update_birds_unauthorized(client):
    response = client.post("/update-birds", json={"birds": [{"name": "Alien"}]})
    assert response.status_code == 401
