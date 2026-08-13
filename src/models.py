from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    favorite_characters: Mapped[list["Character"]] = relationship("Character", secondary="favorite_characters", back_populates="favorited_by")
    favorite_planets: Mapped[list["Planet"]] = relationship("Planet", secondary="favorite_planets", back_populates="favorited_by")
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "favorite_characters": [character.serialize() for character in self.favorite_characters],
            "favorite_planets": [planet.serialize() for planet in self.favorite_planets]
        }

class Character(db.Model):
    character_id: Mapped[int] = mapped_column(primary_key=True)
    url_image: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    race: Mapped[str] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    ki: Mapped[int] = mapped_column(nullable=True)
    max_ki: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    affiliation: Mapped[str] = mapped_column(nullable=True)
    origin_planet_id: Mapped[int] = mapped_column(ForeignKey('planet.planet_id'), nullable=True)
    favorited_by: Mapped[list["User"]] = relationship("User", secondary="favorite_characters", back_populates="favorite_characters")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="characters")

    def serialize(self):
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
    planet_id: Mapped[int] = mapped_column(primary_key=True)
    url_image: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    is_destroyed: Mapped[bool] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    favorited_by: Mapped[list["User"]] = relationship("User", secondary="favorite_planets", back_populates="favorite_planets")
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="planet")

    def serialize(self):
        return {
            "planet_id": self.planet_id,
            "url_image": self.url_image,
            "name": self.name,
            "is_destroyed": self.is_destroyed,
            "description": self.description,
            "characters": [character.serialize() for character in self.characters]
        }

favorite_characters = Table(
    'favorite_characters',
    db.metadata,
    Column('user_id', ForeignKey('user.user_id'), primary_key=True),
    Column('character_id', ForeignKey('character.character_id'), primary_key=True)
)

favorite_planets = Table(
    'favorite_planets',
    db.metadata,
    Column('user_id', ForeignKey('user.user_id'), primary_key=True),
    Column('planet_id', ForeignKey('planet.planet_id'), primary_key=True)
)