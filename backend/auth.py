from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from app import get_mongo  # ✅ moved inside the function
    mongo = get_mongo()

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists.")
            return redirect(url_for('auth.register'))

        mongo.db.users.insert_one({'username': username, 'password': password, 'money': 0, 'birds': []})
        flash("Registered successfully.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import get_mongo  # ✅ again, import here
    mongo = get_mongo()

    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('game.dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
