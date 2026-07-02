from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


found_item_colors = Table(
    "found_item_colors",
    Base.metadata,
    Column("found_item_id", Integer, ForeignKey("found_items.id", ondelete="CASCADE"), primary_key=True),
    Column("color_id", Integer, ForeignKey("colors.id", ondelete="CASCADE"), primary_key=True),
)


class MetroStation(Base):
    __tablename__ = "metro_stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    line: Mapped[str] = mapped_column(String(120))
    nearby_stations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    interchange_nodes: Mapped[list[str]] = mapped_column(JSONB, default=list)

    found_items: Mapped[list["FoundItem"]] = relationship(back_populates="station")


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    found_items: Mapped[list["FoundItem"]] = relationship(back_populates="storage")


class Color(Base):
    __tablename__ = "colors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)

    found_items: Mapped[list["FoundItem"]] = relationship(
        secondary=found_item_colors,
        back_populates="colors",
    )


class FoundItem(Base):
    __tablename__ = "found_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    public_description: Mapped[str] = mapped_column(Text)
    private_features: Mapped[list[str]] = mapped_column(JSONB, default=list)
    category: Mapped[str] = mapped_column(String(80))
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    found_date: Mapped[date] = mapped_column(Date)
    station_id: Mapped[int] = mapped_column(ForeignKey("metro_stations.id"))
    storage_id: Mapped[int] = mapped_column(ForeignKey("storage_locations.id"))
    status: Mapped[str] = mapped_column(String(40), default="available")
    description_embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

    station: Mapped[MetroStation] = relationship(back_populates="found_items")
    storage: Mapped[StorageLocation] = relationship(back_populates="found_items")
    colors: Mapped[list[Color]] = relationship(
        secondary=found_item_colors,
        back_populates="found_items",
    )


class LostRequest(Base):
    __tablename__ = "lost_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    lost_date: Mapped[date] = mapped_column(Date)
    station_id: Mapped[int] = mapped_column(ForeignKey("metro_stations.id"))
    normalized_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    query_embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RequestMatch(Base):
    __tablename__ = "request_matches"

    request_id: Mapped[int] = mapped_column(ForeignKey("lost_requests.id", ondelete="CASCADE"), primary_key=True)
    found_item_id: Mapped[int] = mapped_column(ForeignKey("found_items.id", ondelete="CASCADE"), primary_key=True)
    score: Mapped[float] = mapped_column(Float)
    matched_by: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
