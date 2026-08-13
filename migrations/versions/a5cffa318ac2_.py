"""Migración inicial: crea la tabla 'user'

Revision ID: a5cffa318ac2
Revises:
Create Date: 2023-10-31 13:53:01.946815

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de revisión usados por Alembic
revision = 'a5cffa318ac2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###
    # Crea la tabla 'user' con su id, email único, contraseña y estado activo
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### fin de los comandos de Alembic ###


def downgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###
    # Revierte la migración eliminando la tabla 'user'
    op.drop_table('user')
    # ### fin de los comandos de Alembic ###
