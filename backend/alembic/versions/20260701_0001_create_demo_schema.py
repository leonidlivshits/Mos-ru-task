"""create demo schema

Revision ID: 20260701_0001
Revises:
Create Date: 2026-07-01
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260701_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "metro_stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("line", sa.String(length=120), nullable=False),
        sa.Column("nearby_stations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("interchange_nodes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )

    op.create_table(
        "storage_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "colors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False, unique=True),
    )

    op.create_table(
        "found_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("public_description", sa.Text(), nullable=False),
        sa.Column("private_features", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("brand", sa.String(length=80), nullable=True),
        sa.Column("found_date", sa.Date(), nullable=False),
        sa.Column("station_id", sa.Integer(), sa.ForeignKey("metro_stations.id"), nullable=False),
        sa.Column("storage_id", sa.Integer(), sa.ForeignKey("storage_locations.id"), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="available"),
        sa.Column("description_embedding", Vector(384), nullable=True),
    )
    op.create_index("ix_found_items_found_date", "found_items", ["found_date"])
    op.create_index("ix_found_items_station_id", "found_items", ["station_id"])
    op.create_index("ix_found_items_status", "found_items", ["status"])

    op.create_table(
        "found_item_colors",
        sa.Column("found_item_id", sa.Integer(), sa.ForeignKey("found_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("color_id", sa.Integer(), sa.ForeignKey("colors.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "lost_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("lost_date", sa.Date(), nullable=False),
        sa.Column("station_id", sa.Integer(), sa.ForeignKey("metro_stations.id"), nullable=False),
        sa.Column("normalized_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("query_embedding", Vector(384), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "request_matches",
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("lost_requests.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("found_item_id", sa.Integer(), sa.ForeignKey("found_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("matched_by", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("request_matches")
    op.drop_table("lost_requests")
    op.drop_table("found_item_colors")
    op.drop_index("ix_found_items_status", table_name="found_items")
    op.drop_index("ix_found_items_station_id", table_name="found_items")
    op.drop_index("ix_found_items_found_date", table_name="found_items")
    op.drop_table("found_items")
    op.drop_table("colors")
    op.drop_table("storage_locations")
    op.drop_table("metro_stations")

