from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.db.models import FoundItem, MetroStation
from app.services.normalization import NormalizedRequest, tokenize


@dataclass(frozen=True)
class FoundItemMatch:
    item: FoundItem
    score: float
    matched_by: list[str]


class MatchingService:
    min_score: float = 0.15

    def find_matches(
        self,
        *,
        normalized_request: NormalizedRequest,
        lost_date: date,
        station: MetroStation,
        candidates: list[FoundItem],
        limit: int = 3,
    ) -> list[FoundItemMatch]:
        scored_matches = [
            match
            for item in candidates
            if (match := self._score_item(normalized_request, lost_date, station, item)).score >= self.min_score
        ]
        return sorted(scored_matches, key=lambda match: (-match.score, match.item.id))[:limit]

    def _score_item(
        self,
        normalized_request: NormalizedRequest,
        lost_date: date,
        station: MetroStation,
        item: FoundItem,
    ) -> FoundItemMatch:
        score = 0.0
        matched_by: list[str] = []

        if normalized_request.category and normalized_request.category == item.category:
            score += 0.3
            matched_by.append("категория")

        if station.id == item.station_id:
            score += 0.25
            matched_by.append("станция")
        elif self._is_nearby_station(station, item):
            score += 0.12
            matched_by.append("близкая станция")

        date_score = self._date_score(lost_date, item.found_date)
        if date_score:
            score += date_score
            matched_by.append("дата")

        item_colors = {color.name for color in item.colors}
        request_colors = set(normalized_request.colors)
        if color_overlap := sorted(item_colors & request_colors):
            score += min(0.15, 0.08 + 0.04 * len(color_overlap))
            matched_by.append("цвет")

        if normalized_request.brand and item.brand and normalized_request.brand.lower() == item.brand.lower():
            score += 0.1
            matched_by.append("бренд")

        word_overlap = self._word_overlap(normalized_request, item)
        if word_overlap:
            score += min(0.1, 0.02 * word_overlap)
            matched_by.append("описание")

        return FoundItemMatch(item=item, score=round(min(score, 1.0), 2), matched_by=matched_by)

    def _date_score(self, lost_date: date, found_date: date) -> float:
        days_delta = abs((found_date - lost_date).days)
        if days_delta == 0:
            return 0.2
        if days_delta <= 2:
            return 0.15
        if days_delta <= 5:
            return 0.08
        return 0.0

    def _is_nearby_station(self, station: MetroStation, item: FoundItem) -> bool:
        item_station = item.station
        return (
            item_station.name in station.nearby_stations
            or station.name in item_station.nearby_stations
            or item_station.name in station.interchange_nodes
            or station.name in item_station.interchange_nodes
        )

    def _word_overlap(self, normalized_request: NormalizedRequest, item: FoundItem) -> int:
        item_tokens = set(tokenize(f"{item.title} {item.description} {item.public_description}"))
        request_tokens = {token for token in normalized_request.tokens if len(token) >= 4}
        return len(item_tokens & request_tokens)
