from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MetroStation


class StationsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_stations(self) -> list[MetroStation]:
        statement = select(MetroStation).order_by(MetroStation.id)
        result = await self.db.execute(statement)
        return list(result.scalars())

    async def get_by_id(self, station_id: int) -> MetroStation | None:
        return await self.db.get(MetroStation, station_id)
