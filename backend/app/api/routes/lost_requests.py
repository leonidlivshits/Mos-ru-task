from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.found_items import FoundItemsRepository
from app.repositories.lost_requests import LostRequestsRepository
from app.repositories.request_matches import RequestMatchesRepository
from app.repositories.stations import StationsRepository
from app.schemas.lost_requests import LostRequestCreate, LostRequestCreated, LostRequestMatch
from app.services.embedding_service import EmbeddingServiceError, OpenRouterEmbeddingService
from app.services.input_guard import InputGuard, InputGuardError
from app.services.matching import MatchingService
from app.services.normalization import NormalizationService
from app.services.response_service import ResponseService

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

    normalized_request = NormalizationService().normalize(description)
    embedding_service = OpenRouterEmbeddingService()
    try:
        query_embedding = await embedding_service.embed_text(description, input_type="search_query")
    except EmbeddingServiceError:
        query_embedding = None

    lost_requests = LostRequestsRepository(db)
    lost_request = await lost_requests.create(
        description=description,
        lost_date=payload.lost_date,
        station_id=station.id,
        normalized_data=normalized_request.as_dict(),
        query_embedding=query_embedding,
    )

    found_items = FoundItemsRepository(db)
    vector_scores: dict[int, float] = {}
    if query_embedding:
        vector_matches = await found_items.list_top_k_by_embedding(query_embedding, limit=10)
        candidates = [item for item, _score in vector_matches]
        vector_scores = {item.id: score for item, score in vector_matches}
    else:
        candidates = []

    if not candidates:
        candidates = await found_items.list_available_for_matching()

    matches = MatchingService().find_matches(
        normalized_request=normalized_request,
        lost_date=payload.lost_date,
        station=station,
        candidates=candidates,
        vector_scores=vector_scores,
        limit=3,
    )

    response_service = ResponseService()
    await RequestMatchesRepository(db).replace_for_request(lost_request.id, matches)
    lost_request = await lost_requests.update_status(
        lost_request,
        response_service.status_for_matches(matches),
    )

    return LostRequestCreated(
        request_id=lost_request.id,
        status=lost_request.status,
        message=response_service.message_for_matches(matches),
        matches=[
            LostRequestMatch(
                item_id=match.item.id,
                title=match.item.title,
                public_description=match.item.public_description,
                score=match.score,
                rule_score=match.rule_score,
                vector_score=match.vector_score,
                matched_by=match.matched_by,
                found_date=match.item.found_date,
                station=match.item.station.name,
                line=match.item.station.line,
                storage=match.item.storage.name,
                colors=[color.name for color in match.item.colors],
            )
            for match in matches
        ],
    )
