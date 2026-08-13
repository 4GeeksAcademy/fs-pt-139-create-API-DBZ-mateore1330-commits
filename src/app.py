"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    users = User.query.all()
    print([user.serialize() for user in users])
    return jsonify([user.serialize() for user in users]), 200



@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    existing_user = db.session.execute(select(User).where(User.email == data['email'])).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    user = User(email=data['email'], password=data['password'], name=data.get('name', ''))

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 201

@app.route('/character', methods=['POST'])
def create_character():
    data = request.get_json()
    if not data.get("name") or not data.get("url_image") or not data.get("race") or not data.get("gender") or not data.get("origin_planet_id"):
        return jsonify({"error": "Name, URL image, race, gender, and origin planet ID are required"}), 400
    character = Character(
        name=data["name"],
        url_image=data.get("url_image"),
        race=data.get("race"),
        gender=data.get("gender"),
        ki=data.get("ki"),
        max_ki=data.get("max_ki"),
        description=data.get("description", ""),
        affiliation=data.get("affiliation", ""),
        origin_planet_id=data.get("origin_planet_id")
    )

    db.session.add(character)
    db.session.commit()

    return jsonify(character.serialize()), 201



    
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
