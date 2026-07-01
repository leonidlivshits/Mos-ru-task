from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import FoundItem


class FoundItemsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_demo_items(self) -> list[FoundItem]:
        statement = (
            select(FoundItem)
            .options(
                joinedload(FoundItem.colors),
                joinedload(FoundItem.station),
                joinedload(FoundItem.storage),
            )
            .order_by(FoundItem.found_date.desc(), FoundItem.id)
        )
        result = await self.db.execute(statement)
        return list(result.unique().scalars())

    async def list_available_for_matching(self) -> list[FoundItem]:
        statement = (
            select(FoundItem)
            .where(FoundItem.status == "available")
            .options(
                joinedload(FoundItem.colors),
                joinedload(FoundItem.station),
                joinedload(FoundItem.storage),
            )
            .order_by(FoundItem.found_date.desc(), FoundItem.id)
        )
        result = await self.db.execute(statement)
        return list(result.unique().scalars())

    async def list_without_embeddings(self) -> list[FoundItem]:
        statement = (
            select(FoundItem)
            .where(FoundItem.description_embedding.is_(None))
            .order_by(FoundItem.id)
        )
        result = await self.db.execute(statement)
        return list(result.scalars())

    async def list_top_k_by_embedding(
        self,
        query_embedding: list[float],
        *,
        limit: int = 10,
    ) -> list[tuple[FoundItem, float]]:
        distance = FoundItem.description_embedding.cosine_distance(query_embedding).label("vector_distance")
        statement = (
            select(FoundItem, distance)
            .where(
                FoundItem.status == "available",
                FoundItem.description_embedding.is_not(None),
            )
            .options(
                joinedload(FoundItem.colors),
                joinedload(FoundItem.station),
                joinedload(FoundItem.storage),
            )
            .order_by(distance)
            .limit(limit)
        )
        result = await self.db.execute(statement)
        rows = result.unique().all()
        return [
            (item, self._distance_to_similarity(vector_distance))
            for item, vector_distance in rows
        ]

    async def update_embeddings(self, items: list[FoundItem], embeddings: list[list[float]]) -> None:
        for item, embedding in zip(items, embeddings, strict=True):
            item.description_embedding = embedding
        await self.db.commit()

    def _distance_to_similarity(self, distance: float) -> float:
        return round(max(0.0, min(1.0, 1.0 - distance)), 4)
