from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.found_items import FoundItemsRepository
from app.schemas.demo import DemoFoundItem

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/found-items", response_model=list[DemoFoundItem])
async def list_demo_found_items(db: AsyncSession = Depends(get_db)) -> list[DemoFoundItem]:
    items = await FoundItemsRepository(db).list_demo_items()
    return [
        DemoFoundItem(
            id=item.id,
            title=item.title,
            public_description=item.public_description,
            category=item.category,
            brand=item.brand,
            colors=[color.name for color in item.colors],
            found_date=item.found_date,
            station=item.station.name,
            line=item.station.line,
            storage=item.storage.name,
            status=item.status,
            has_embedding=item.description_embedding is not None,
        )
        for item in items
    ]
