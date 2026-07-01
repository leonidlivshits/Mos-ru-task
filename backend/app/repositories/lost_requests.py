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
        normalized_data: dict[str, object] | None = None,
        query_embedding: list[float] | None = None,
    ) -> LostRequest:
        lost_request = LostRequest(
            description=description,
            lost_date=lost_date,
            station_id=station_id,
            normalized_data=normalized_data or {},
            query_embedding=query_embedding,
            status="created",
        )
        self.db.add(lost_request)
        await self.db.commit()
        await self.db.refresh(lost_request)
        return lost_request

    async def get_by_id(self, request_id: int) -> LostRequest | None:
        return await self.db.get(LostRequest, request_id)

    async def update_status(self, lost_request: LostRequest, status: str) -> LostRequest:
        lost_request.status = status
        await self.db.commit()
        await self.db.refresh(lost_request)
        return lost_request
