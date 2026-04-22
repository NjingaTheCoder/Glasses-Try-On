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

# Declare the enum once — reused in upgrade() and downgrade()
_glasses_shape = PgEnum(
    "round", "square", "aviator", "cat-eye", "oval", "rectangle",
    name="glasses_shape",
)


def upgrade() -> None:
    # checkfirst=True makes this a no-op if the type already exists,
    # so the migration is safe to re-run or apply to a DB that already
    # has the enum from a previous failed attempt.
    _glasses_shape.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("brand", sa.String(200), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        # create_type=False — we already created the enum above with checkfirst
        sa.Column(
            "shape",
            sa.Enum(
                "round", "square", "aviator", "cat-eye", "oval", "rectangle",
                name="glasses_shape",
                create_type=False,
            ),
            nullable=False,
        ),
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
    # checkfirst=True so this is safe even if the type was already dropped
    _glasses_shape.drop(op.get_bind(), checkfirst=True)
