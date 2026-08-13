"""Ajusta la obligatoriedad de campos: origin_planet_id y user.name

Revision ID: c170fca6e81c
Revises: 1e08c24d66e3
Create Date: 2026-08-13 20:10:19.406500

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de revisión usados por Alembic
revision = 'c170fca6e81c'
down_revision = '1e08c24d66e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###

    # 'origin_planet_id' pasa a ser obligatorio: todo personaje debe tener planeta de origen
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.alter_column('origin_planet_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # 'name' del usuario pasa a ser opcional
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### fin de los comandos de Alembic ###


def downgrade():
    # ### comandos generados automáticamente por Alembic - ¡revisar antes de usar! ###

    # Revierte 'name' del usuario a obligatorio
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # Revierte 'origin_planet_id' a opcional
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.alter_column('origin_planet_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### fin de los comandos de Alembic ###
