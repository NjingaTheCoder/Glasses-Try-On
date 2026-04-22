"""create products and uploads tables

Revision ID: 0001
Revises:
Create Date: 2026-04-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_SHAPE_VALUES = ("round", "square", "aviator", "cat-eye", "oval", "rectangle")

# create_type=False — used in the column definition so SQLAlchemy never tries
# to auto-create the type; the raw DDL below owns creation instead.
_glasses_shape_col = PgEnum(*_SHAPE_VALUES, name="glasses_shape", create_type=False)


def upgrade() -> None:
    # IF NOT EXISTS makes this safe whether the type is brand-new or was left
    # behind by a previously failed migration run.
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'glasses_shape') THEN "
        "CREATE TYPE glasses_shape AS ENUM ("
        + ", ".join(f"'{v}'" for v in _SHAPE_VALUES)
        + "); "
        "END IF; "
        "END $$"
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("brand", sa.String(200), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("shape", _glasses_shape_col, nullable=False),
        sa.Column("color", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("bridge_x", sa.Numeric(6, 5), nullable=False),
        sa.Column("bridge_y", sa.Numeric(6, 5), nullable=False),
        sa.Column("left_temple_x", sa.Numeric(6, 5), nullable=False),
        sa.Column("left_temple_y", sa.Numeric(6, 5), nullable=False),
        sa.Column("right_temple_x", sa.Numeric(6, 5), nullable=False),
        sa.Column("right_temple_y", sa.Numeric(6, 5), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "uploads",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_session_id", sa.String(100), nullable=False),
        sa.Column("firebase_url", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("uploads")
    op.drop_table("products")
    op.execute(
        "DO $$ BEGIN "
        "IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'glasses_shape') THEN "
        "DROP TYPE glasses_shape; "
        "END IF; "
        "END $$"
    )
