from flask import Flask, redirect
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, session, redirect, url_for, send_from_directory, jsonify, request
from bson.objectid import ObjectId
import subprocess
import shutil

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo()

def get_mongo():
    return mongo

mongo.init_app(app)

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # from app import get_mongo  # ✅ moved inside the function
    # mongo = get_mongo()

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

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # from app import get_mongo  # ✅ again, import here
    # mongo = get_mongo()

    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('game.dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

app.register_blueprint(auth)

@app.route('/')
def home():
    return redirect('/dashboard')

def register_blueprints():
    import backend.game as game
    app.register_blueprint(game.bp)

register_blueprints()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
