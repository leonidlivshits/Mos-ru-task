from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.lost_requests import LostRequestsRepository
from app.repositories.stations import StationsRepository
from app.schemas.lost_requests import LostRequestCreate, LostRequestCreated
from app.services.input_guard import InputGuard, InputGuardError

router = APIRouter(tags=["lost_requests"])


@router.post(
    "/lost-requests",
    response_model=LostRequestCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_lost_request(
    payload: LostRequestCreate,
    db: AsyncSession = Depends(get_db),
) -> LostRequestCreated:
    guard = InputGuard()

    try:
        description = guard.clean_description(payload.description)
        guard.validate_lost_date(payload.lost_date)
    except InputGuardError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    station = await StationsRepository(db).get_by_id(payload.station_id)
    if station is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Станция не найдена",
        )

    lost_request = await LostRequestsRepository(db).create(
        description=description,
        lost_date=payload.lost_date,
        station_id=station.id,
    )
    return LostRequestCreated(request_id=lost_request.id, status=lost_request.status)
