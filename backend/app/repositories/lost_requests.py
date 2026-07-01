from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LostRequest


class LostRequestsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        description: str,
        lost_date: date,
        station_id: int,
    ) -> LostRequest:
        lost_request = LostRequest(
            description=description,
            lost_date=lost_date,
            station_id=station_id,
            normalized_data={},
            status="created",
        )
        self.db.add(lost_request)
        await self.db.commit()
        await self.db.refresh(lost_request)
        return lost_request
