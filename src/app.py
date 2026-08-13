"""
Este módulo se encarga de arrancar el servidor de la API, cargar la base de
datos y registrar todos los endpoints de la aplicación.
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
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos: si existe la variable de entorno
# DATABASE_URL se usa esa conexión (Postgres), si no, se usa SQLite local.
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


# ======================================================================
#   MANEJO DE ERRORES Y MAPA DEL SITIO
# ======================================================================

# Gestiona y serializa los errores de la API como un objeto JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Genera un mapa con todos los endpoints disponibles en la API
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# ======================================================================
#   RUTAS POST - CREACIÓN DE RECURSOS
# ======================================================================

# --- Usuario ---

# Crea un nuevo usuario a partir del email, la contraseña y (opcionalmente) el nombre
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = db.session.execute(select(User).where(User.email == data['email'])).scalar_one()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    user = User(email=data['email'], password=data['password'], name=data.get('name', ''))

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 201


# --- Personajes ---

# Crea un nuevo personaje, comprobando antes que estén los campos obligatorios
@app.route('/characters', methods=['POST'])
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


# --- Planetas ---

# Crea un nuevo planeta, comprobando antes que estén los campos obligatorios
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data.get("name") or not data.get("url_image") or not data.get("is_destroyed"):
        return jsonify({"error": "Name, URL image, and is_destroyed are required"}), 400
    planet = Planet(
        name=data["name"],
        url_image=data.get("url_image"),
        is_destroyed=data.get("is_destroyed"),
        description=data.get("description", "")
    )

    db.session.add(planet)
    db.session.commit()

    return jsonify(planet.serialize()), 201


# --- Personajes favoritos ---

# Añade un personaje a la lista de favoritos de un usuario
@app.route("/users/<int:user_id>/favorites-characters/<int:character_id>", methods=["POST"])
def add_favorite_character(user_id, character_id):
    user = db.session.get(User, user_id)
    character = db.session.get(Character, character_id)

    if not user or not character:
        return jsonify({"error": "User or Character not found"}), 404

    if character not in user.favorite_characters:
        user.favorite_characters.append(character)
        db.session.commit()
        return jsonify(user.serialize()), 200

    return jsonify({"error": "Character already in favorites"}), 400


# --- Planetas favoritos ---

# Añade un planeta a la lista de favoritos de un usuario
@app.route('/users/<int:user_id>/favorites-planets/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = db.session.get(User, user_id)
    planet = db.session.get(Planet, planet_id)

    if not user or not planet:
        return jsonify({"error": "User or Planet not found"}), 404

    if planet not in user.favorite_planets:
        user.favorite_planets.append(planet)
        db.session.commit()
        return jsonify(user.serialize()), 200

    return jsonify({"error": "Planet already in favorites"}), 400


# ======================================================================
#   RUTAS GET - CONSULTA DE RECURSOS
# ======================================================================

# --- Usuario ---

# Devuelve la lista completa de usuarios registrados
@app.route('/users', methods=['GET'])
def get_all_users():

    users = User.query.all()
    print([user.serialize() for user in users])
    return jsonify([user.serialize() for user in users]), 200


# Devuelve un usuario concreto a partir de su id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200


# --- Personajes ---

# Devuelve la lista completa de personajes
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200


# Devuelve un personaje concreto a partir de su id
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = db.session.get(Character, character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200


# --- Planetas ---

# Devuelve la lista completa de planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


# Devuelve un planeta concreto a partir de su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


# --- Personajes favoritos ---

# Devuelve un personaje favorito concreto de un usuario, comprobando que
# tanto el usuario como el personaje existan y que el personaje esté en favoritos
@app.route('/users/<int:user_id>/favorites-characters/<int:character_id>', methods=['GET'])
def get_favorite_character(user_id, character_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    character = db.session.get(Character, character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    if character not in user.favorite_characters:
        return jsonify({"error": "Character is not in user's favorites"}), 404
    return jsonify(character.serialize()), 200


# --- Planetas favoritos ---

# Devuelve un planeta favorito concreto de un usuario, comprobando que
# tanto el usuario como el planeta existan y que el planeta esté en favoritos
@app.route('/users/<int:user_id>/favorites-planets/<int:planet_id>', methods=['GET'])
def get_favorite_planet(user_id, planet_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    if planet not in user.favorite_planets:
        return jsonify({"error": "Planet is not in user's favorites"}), 404
    return jsonify(planet.serialize()), 200


# ======================================================================
#   RUTAS PUT - ACTUALIZACIÓN DE RECURSOS
# ======================================================================

# --- Usuario ---

# Actualiza los datos de un usuario existente (solo los campos que se envíen)
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)

    db.session.commit()

    return jsonify(user.serialize()), 200


# --- Personajes ---

# Actualiza los datos de un personaje existente (solo los campos que se envíen)
@app.route('/characters/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    data = request.get_json()
    character = db.session.get(Character, character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    character.name = data.get('name', character.name)
    character.url_image = data.get('url_image', character.url_image)
    character.race = data.get('race', character.race)
    character.gender = data.get('gender', character.gender)
    character.ki = data.get('ki', character.ki)
    character.max_ki = data.get('max_ki', character.max_ki)
    character.description = data.get('description', character.description)
    character.affiliation = data.get('affiliation', character.affiliation)
    character.origin_planet_id = data.get('origin_planet_id', character.origin_planet_id)

    db.session.commit()

    return jsonify(character.serialize()), 200


# --- Planetas ---

# Actualiza los datos de un planeta existente (solo los campos que se envíen)
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    planet.name = data.get('name', planet.name)
    planet.url_image = data.get('url_image', planet.url_image)
    planet.is_destroyed = data.get('is_destroyed', planet.is_destroyed)
    planet.description = data.get('description', planet.description)

    db.session.commit()

    return jsonify(planet.serialize()), 200


# ======================================================================
#   RUTAS DELETE - ELIMINACIÓN DE RECURSOS
# ======================================================================

# --- Usuario ---

# Elimina un usuario a partir de su id
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify(user.serialize()), 200


# --- Personajes ---

# Elimina un personaje a partir de su id
@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = db.session.get(Character, character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify(character.serialize()), 200


# --- Planetas ---

# Elimina un planeta a partir de su id
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 200


# --- Personajes favoritos ---

# Elimina un personaje de la lista de favoritos de un usuario
@app.route('/users/<int:user_id>/favorites-characters/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(user_id, character_id):
    user = db.session.get(User, user_id)
    character = db.session.get(Character, character_id)

    if not user or not character:
        return jsonify({"error": "User or Character not found"}), 404

    if character in user.favorite_characters:
        user.favorite_characters.remove(character)
        db.session.commit()
        return jsonify(user.serialize()), 200

    return jsonify({"error": "Character not in favorites"}), 400


# --- Planetas favoritos ---

# Elimina un planeta de la lista de favoritos de un usuario
@app.route('/users/<int:user_id>/favorites-planets/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(user_id, planet_id):
    user = db.session.get(User, user_id)
    planet = db.session.get(Planet, planet_id)

    if not user or not planet:
        return jsonify({"error": "User or Planet not found"}), 404

    if planet in user.favorite_planets:
        user.favorite_planets.remove(planet)
        db.session.commit()
        return jsonify(user.serialize()), 200

    return jsonify({"error": "Planet not in favorites"}), 400


# Esto solo se ejecuta si se lanza el archivo directamente con `$ python src/app.py`
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
