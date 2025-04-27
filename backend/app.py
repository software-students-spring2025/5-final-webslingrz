from flask import Flask, redirect
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo()

def get_mongo():
    return mongo

mongo.init_app(app)

@app.route('/')
def home():
    return redirect('/dashboard')

def register_blueprints():
    import auth
    import game
    app.register_blueprint(auth.bp)
    app.register_blueprint(game.bp)

register_blueprints()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
