from flask import Blueprint, render_template, session, redirect, url_for
from bson.objectid import ObjectId

bp = Blueprint('game', __name__)

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    from app import get_mongo  # ✅ delayed import
    mongo = get_mongo()

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('dashboard.html', money=user.get('money', 0))

@bp.route('/birds')
def birds():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    from app import get_mongo  # ✅ delayed import
    mongo = get_mongo()

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    return render_template('birds.html', birds=user.get('birds', []))
