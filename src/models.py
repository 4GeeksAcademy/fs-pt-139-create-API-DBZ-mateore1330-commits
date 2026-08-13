"""
Este módulo define los modelos de la base de datos y sus relaciones:
usuarios, personajes, planetas y las tablas intermedias de favoritos.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    """Representa a un usuario de la aplicación."""

    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    # Relación muchos a muchos con Character a través de la tabla intermedia favorite_characters
    favorite_characters: Mapped[list["Character"]] = relationship("Character", secondary="favorite_characters", back_populates="favorited_by")
    # Relación muchos a muchos con Planet a través de la tabla intermedia favorite_planets
    favorite_planets: Mapped[list["Planet"]] = relationship("Planet", secondary="favorite_planets", back_populates="favorited_by")

    def serialize(self):
        """Convierte el usuario (y sus favoritos) a un diccionario listo para JSON."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "favorite_characters": [character.serialize() for character in self.favorite_characters],
            "favorite_planets": [planet.serialize() for planet in self.favorite_planets]
        }


class Character(db.Model):
    """Representa a un personaje del universo Dragon Ball."""

    character_id: Mapped[int] = mapped_column(primary_key=True)
    url_image: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    race: Mapped[str] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    ki: Mapped[int] = mapped_column(nullable=True)
    max_ki: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    affiliation: Mapped[str] = mapped_column(nullable=True)
    # Planeta de origen del personaje (clave foránea obligatoria)
    origin_planet_id: Mapped[int] = mapped_column(ForeignKey('planet.planet_id'), nullable=False)

    # Usuarios que tienen a este personaje como favorito
    favorited_by: Mapped[list["User"]] = relationship("User", secondary="favorite_characters", back_populates="favorite_characters")
    # Planeta al que pertenece el personaje
    planet: Mapped["Planet"] = relationship("Planet", back_populates="characters")

    def serialize(self):
        """Convierte el personaje a un diccionario listo para JSON, incluyendo su planeta de origen."""
        origin_planet = None
        if self.origin_planet_id:
            origin_planet = {
                "planet_id": self.origin_planet_id,
                "name": self.planet.name,
            }

        return {
            "character_id": self.character_id,
            "url_image": self.url_image,
            "name": self.name,
            "race": self.race,
            "gender": self.gender,
            "ki": self.ki,
            "max_ki": self.max_ki,
            "description": self.description,
            "affiliation": self.affiliation,
            "origin_planet": origin_planet

        }


class Planet(db.Model):
    """Representa a un planeta del universo Dragon Ball."""

    planet_id: Mapped[int] = mapped_column(primary_key=True)
    url_image: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    is_destroyed: Mapped[bool] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    # Usuarios que tienen a este planeta como favorito
    favorited_by: Mapped[list["User"]] = relationship("User", secondary="favorite_planets", back_populates="favorite_planets")
    # Personajes originarios de este planeta
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="planet")

    def serialize(self):
        """Convierte el planeta a un diccionario listo para JSON, incluyendo sus personajes."""
        return {
            "planet_id": self.planet_id,
            "url_image": self.url_image,
            "name": self.name,
            "is_destroyed": self.is_destroyed,
            "description": self.description,
            "characters": [character.serialize() for character in self.characters]
        }


# ======================================================================
#   TABLAS INTERMEDIAS (RELACIONES MUCHOS A MUCHOS)
# ======================================================================

# Tabla intermedia que guarda los personajes favoritos de cada usuario
favorite_characters = Table(
    'favorite_characters',
    db.metadata,
    Column('user_id', ForeignKey('user.user_id'), primary_key=True),
    Column('character_id', ForeignKey('character.character_id'), primary_key=True)
)

# Tabla intermedia que guarda los planetas favoritos de cada usuario
favorite_planets = Table(
    'favorite_planets',
    db.metadata,
    Column('user_id', ForeignKey('user.user_id'), primary_key=True),
    Column('planet_id', ForeignKey('planet.planet_id'), primary_key=True)
)
