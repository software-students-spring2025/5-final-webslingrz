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
game = Blueprint('game', __name__)

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

# Directory structure
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(CURRENT_DIR, "bird_game")
BUILD_DIR = os.path.join(GAME_DIR, "build")
WEB_DIR = os.path.join(BUILD_DIR, "web")

@game.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # from app import get_mongo
    # mongo = get_mongo()
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('dashboard.html', money=user.get('money', 0))

@game.route('/birds')
def birds():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # from app import get_mongo
    # mongo = get_mongo()
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('birds.html', birds=user.get('birds', []))

@game.route('/play')
def play():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Serve the index.html file from the build directory

    # print(f"WEB_DIR path: {WEB_DIR}")
    # print(f"Full path: {os.path.join(WEB_DIR, 'index.html')}")
    # print(f"File exists: {os.path.exists(os.path.join(WEB_DIR, 'index.html'))}")
    # print(f"Directory contents: {os.listdir(WEB_DIR) if os.path.exists(WEB_DIR) else 'Directory not found'}")

    return send_from_directory(WEB_DIR, 'index.html')

@game.route('/game-assets/<path:path>')
def serve_game_assets(path):
    # Serve the asset files from the build directory
    return send_from_directory(WEB_DIR, path)

@game.route('/<path:filename>')
def serve_root_files(filename):
    if os.path.exists(os.path.join(WEB_DIR, filename)):
        return send_from_directory(WEB_DIR, filename)
    else:
        return "File not found", 404

@game.route('/build-game', methods=['POST'])
def build_game():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    try:
        # Create the build directory if it doesn't exist
        os.makedirs(BUILD_DIR, exist_ok=True)
        
        # Run the pygbag build command
        result = subprocess.run(
            ["pygbag", "--build", GAME_DIR], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "message": f"Build failed: {result.stderr}"
            }), 500
            
        return jsonify({
            "success": True,
            "message": "Game built successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/')
def home():
    return redirect('/dashboard')

app.register_blueprint(auth)
app.register_blueprint(game)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
