"""Añade personajes, planetas y favoritos, y adapta la tabla 'user'

Revision ID: 1e08c24d66e3
Revises: a5cffa318ac2
Create Date: 2026-08-13 19:10:33.955250

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de revisión usados por Alembic
revision = '1e08c24d66e3'
down_revision = 'a5cffa318ac2'
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###

    # Adapta la tabla 'user': renombra 'id' a 'user_id', añade el campo 'name'
    # y elimina el campo 'is_active' (que ya no se utiliza)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('id', new_column_name='user_id')
        batch_op.add_column(sa.Column('name', sa.String(), nullable=False))
        batch_op.drop_column('is_active')

    # Crea la tabla 'planet' con sus datos básicos
    op.create_table('planet',
                    sa.Column('planet_id', sa.Integer(), nullable=False),
                    sa.Column('url_image', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('is_destroyed', sa.Boolean(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('planet_id')
                    )
    # Crea la tabla 'character', relacionada con su planeta de origen
    op.create_table('character',
                    sa.Column('character_id', sa.Integer(), nullable=False),
                    sa.Column('url_image', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('race', sa.String(), nullable=False),
                    sa.Column('gender', sa.String(), nullable=False),
                    sa.Column('ki', sa.Integer(), nullable=True),
                    sa.Column('max_ki', sa.Integer(), nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('affiliation', sa.String(), nullable=True),
                    sa.Column('origin_planet_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['origin_planet_id'], [
                                            'planet.planet_id'], ),
                    sa.PrimaryKeyConstraint('character_id')
                    )
    # Crea la tabla intermedia de planetas favoritos (relación usuario-planeta)
    op.create_table('favorite_planets',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('planet_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['planet_id'], ['planet.planet_id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'planet_id')
                    )
    # Crea la tabla intermedia de personajes favoritos (relación usuario-personaje)
    op.create_table('favorite_characters',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('character_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['character_id'], ['character.character_id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'character_id')
                    )

    # ### fin de los comandos de Alembic ###


def downgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###

    # Elimina las tablas creadas en esta migración, en orden inverso por las
    # dependencias entre claves foráneas
    op.drop_table('favorite_characters')
    op.drop_table('favorite_planets')
    op.drop_table('character')
    op.drop_table('planet')

    # Revierte los cambios sobre la tabla 'user': recupera 'is_active',
    # elimina 'name' y renombra 'user_id' de nuevo a 'id'
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
        batch_op.drop_column('name')
        batch_op.alter_column('user_id', new_column_name='id')
    # ### fin de los comandos de Alembic ###
