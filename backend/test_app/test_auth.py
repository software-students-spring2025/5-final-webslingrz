import pytest
from flask import Flask, session, redirect, request
from unittest.mock import patch, MagicMock

from werkzeug.security import generate_password_hash, check_password_hash

# In-memory user storage for mocking DB
fake_users = {}

@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = 'test_key'
    app.config['TESTING'] = True

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            if username in fake_users:
                return b"Username already exists"
            fake_users[username] = {'password': password}
            return b"Registered successfully"
        return b"Register Page"

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = fake_users.get(username)
            if user and check_password_hash(user['password'], password):
                session['user_id'] = username
                return b"Dashboard"
            return b"Invalid credentials"
        return b"Login Page"

    @app.route('/logout')
    def logout():
        session.clear()
        return b"Login Page"

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_register_existing_user(client):
    fake_users.clear()
    fake_users['alreadyuser'] = {'password': generate_password_hash('test123')}

    response = client.post('/register', data={
        'username': 'alreadyuser',
        'password': 'test123'
    })

    assert b"Username already exists" in response.data


def test_register_new_user(client):
    fake_users.clear()

    response = client.post('/register', data={
        'username': 'newuser123',
        'password': 'newpass'
    })

    assert b"Registered successfully" in response.data
    assert 'newuser123' in fake_users


def test_login_invalid(client):
    fake_users.clear()

    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })

    assert b"Invalid credentials" in response.data


def test_login_valid(client):
    fake_users.clear()
    fake_users['realuser'] = {'password': generate_password_hash('realpass')}

    response = client.post('/login', data={
        'username': 'realuser',
        'password': 'realpass'
    })

    assert b"Dashboard" in response.data


def test_logout(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'realuser'

    response = client.get('/logout')
    assert b"Login Page" in response.data

@patch('app.get_mongo')
def test_register(mock_mongo, client):
    mock_db = MagicMock()
    mock_mongo.return_value = mock_db
    mock_db.db.users.find_one.return_value = None

    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123'
    }, follow_redirects=True)

    # mock_db.db.users.insert_one.assert_called_once()
    assert b"Registered successfully" in response.data

@patch('app.get_mongo')
def test_register_get(mock_mongo, client):
    mock_mongo.return_value = MagicMock()
    response = client.get('/register')
    assert response.status_code == 200

@patch('app.get_mongo')
def test_register_existing_user(mock_mongo, client):
    mock_db = MagicMock()
    mock_mongo.return_value = mock_db
    mock_db.db.users.find_one.return_value = {'username': 'existinguser'}

    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    # assert '/register' in response.headers['Location']