from datetime import date

from app.db.models import Color, FoundItem, MetroStation, StorageLocation
from app.services.matching import MatchingService
from app.services.normalization import NormalizationService


def test_normalization_extracts_category_color_and_brand() -> None:
    normalized = NormalizationService().normalize("Потерял черный рюкзак Nike на станции")

    assert normalized.category == "рюкзак"
    assert normalized.colors == ["черный"]
    assert normalized.brand == "Nike"


def test_normalization_extracts_ball_category() -> None:
    normalized = NormalizationService().normalize("Потерял футбольный мяч")

    assert normalized.category == "мяч"


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


def test_matching_combines_rule_score_with_vector_score() -> None:
    station = MetroStation(id=1, name="Тверская", line="Замоскворецкая", nearby_stations=[], interchange_nodes=[])
    storage = StorageLocation(id=1, name="Склад забытых вещей", address=None)
    item = FoundItem(
        id=1,
        title="Черный рюкзак Nike",
        description="Черный городской рюкзак Nike",
        public_description="Черный рюкзак Nike, найден на станции.",
        private_features=[],
        category="рюкзак",
        brand="Nike",
        found_date=date(2026, 6, 30),
        station_id=1,
        storage_id=1,
        status="available",
        station=station,
        storage=storage,
        colors=[],
    )
    normalized = NormalizationService().normalize("Потерял черный рюкзак")

    matches = MatchingService().find_matches(
        normalized_request=normalized,
        lost_date=date(2026, 6, 30),
        station=station,
        candidates=[item],
        vector_scores={1: 1.0},
    )

    assert matches[0].vector_score == 1.0
    assert matches[0].rule_score < matches[0].score
    assert "semantic" in matches[0].matched_by


def test_matching_rejects_different_category_even_with_same_station_and_date() -> None:
    station = MetroStation(id=1, name="Балтийская", line="МЦК", nearby_stations=[], interchange_nodes=[])
    storage = StorageLocation(id=1, name="Склад забытых вещей", address=None)
    item = FoundItem(
        id=1,
        title="Красная сумка Puma",
        description="Красная спортивная сумка, найдена на станции",
        public_description="Красная спортивная сумка, найдена на станции.",
        private_features=[],
        category="сумка",
        brand="Puma",
        found_date=date(2026, 6, 30),
        station_id=1,
        storage_id=1,
        status="available",
        station=station,
        storage=storage,
        colors=[],
    )
    normalized = NormalizationService().normalize("Потерял футбольный мяч")

    matches = MatchingService().find_matches(
        normalized_request=normalized,
        lost_date=date(2026, 6, 30),
        station=station,
        candidates=[item],
        vector_scores={1: 0.25},
    )

    assert matches == []
