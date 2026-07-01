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
