from datetime import date

from app.db.models import Color, FoundItem, MetroStation, StorageLocation
from app.services.matching import MatchingService
from app.services.normalization import NormalizationService


def test_normalization_extracts_category_color_and_brand() -> None:
    normalized = NormalizationService().normalize("Потерял черный рюкзак Nike на станции")

    assert normalized.category == "рюкзак"
    assert normalized.colors == ["черный"]
    assert normalized.brand == "Nike"


def test_matching_scores_category_station_date_color_and_brand() -> None:
    station = MetroStation(id=1, name="Тверская", line="Замоскворецкая", nearby_stations=[], interchange_nodes=[])
    storage = StorageLocation(id=1, name="Склад забытых вещей", address=None)
    black = Color(id=1, name="черный")
    item = FoundItem(
        id=1,
        title="Черный рюкзак Nike",
        description="Черный городской рюкзак Nike, внутри синяя папка",
        public_description="Черный рюкзак Nike, найден на станции.",
        private_features=["синяя папка"],
        category="рюкзак",
        brand="Nike",
        found_date=date(2026, 6, 30),
        station_id=1,
        storage_id=1,
        status="available",
        station=station,
        storage=storage,
        colors=[black],
    )
    normalized = NormalizationService().normalize("Потерял черный рюкзак Nike")

    matches = MatchingService().find_matches(
        normalized_request=normalized,
        lost_date=date(2026, 6, 30),
        station=station,
        candidates=[item],
    )

    assert len(matches) == 1
    assert matches[0].item.id == 1
    assert matches[0].score >= 0.9
    assert set(matches[0].matched_by) >= {"категория", "станция", "дата", "цвет", "бренд"}
