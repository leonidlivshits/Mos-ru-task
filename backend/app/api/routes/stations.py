from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.stations import StationsRepository
from app.schemas.stations import StationRead

router = APIRouter(tags=["stations"])


@router.get("/stations", response_model=list[StationRead])
async def list_stations(db: AsyncSession = Depends(get_db)) -> list[StationRead]:
    stations = await StationsRepository(db).list_stations()
    return [StationRead.model_validate(station) for station in stations]
