from flask import Blueprint, render_template, session, redirect, url_for, send_from_directory, jsonify, request
from bson.objectid import ObjectId
import os
import subprocess
import shutil

bp = Blueprint('game', __name__)

# Directory structure
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(CURRENT_DIR, "bird_game")
BUILD_DIR = os.path.join(GAME_DIR, "build")
WEB_DIR = os.path.join(BUILD_DIR, "web")

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    from app import get_mongo
    mongo = get_mongo()
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('dashboard.html', money=user.get('money', 0))

@bp.route('/birds')
def birds():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    from app import get_mongo
    mongo = get_mongo()
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('birds.html', birds=user.get('birds', []))

@bp.route('/play')
def play():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Serve the index.html file from the build directory

    print(f"WEB_DIR path: {WEB_DIR}")
    print(f"Full path: {os.path.join(WEB_DIR, 'index.html')}")
    print(f"File exists: {os.path.exists(os.path.join(WEB_DIR, 'index.html'))}")
    print(f"Directory contents: {os.listdir(WEB_DIR) if os.path.exists(WEB_DIR) else 'Directory not found'}")

    return send_from_directory(WEB_DIR, 'index.html')

@bp.route('/game-assets/<path:path>')
def serve_game_assets(path):
    # Serve the asset files from the build directory
    return send_from_directory(WEB_DIR, path)

@bp.route('/<path:filename>')
def serve_root_files(filename):
    if os.path.exists(os.path.join(WEB_DIR, filename)):
        return send_from_directory(WEB_DIR, filename)
    else:
        return "File not found", 404

@bp.route('/build-game', methods=['POST'])
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

@bp.route('/update-money', methods=['POST'])
def update_money():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    if not data or 'money' not in data:
        return jsonify({"success": False, "message": "Invalid data"}), 400
    
    try:
        from app import get_mongo
        mongo = get_mongo()
        
        # Update the user's money
        mongo.db.users.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"money": data['money']}}
        )
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route('/update-birds', methods=['POST'])
def update_birds():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    if not data or 'birds' not in data:
        return jsonify({"success": False, "message": "Invalid data"}), 400
    
    try:
        from app import get_mongo
        mongo = get_mongo()
        
        # Update the user's birds collection
        mongo.db.users.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"birds": data['birds']}}
        )
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500