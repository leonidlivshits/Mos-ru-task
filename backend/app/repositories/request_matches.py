from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RequestMatch
from app.services.matching import FoundItemMatch


class RequestMatchesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def replace_for_request(self, request_id: int, matches: list[FoundItemMatch]) -> None:
        await self.db.execute(delete(RequestMatch).where(RequestMatch.request_id == request_id))

        self.db.add_all(
            [
                RequestMatch(
                    request_id=request_id,
                    found_item_id=match.item.id,
                    score=match.score,
                    matched_by=match.matched_by,
                )
                for match in matches
            ]
        )

    async def exists(self, request_id: int, found_item_id: int) -> bool:
        statement = select(RequestMatch).where(
            RequestMatch.request_id == request_id,
            RequestMatch.found_item_id == found_item_id,
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none() is not None
