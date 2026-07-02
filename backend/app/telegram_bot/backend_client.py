from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx


class BackendApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class Station:
    id: int
    name: str
    line: str


@dataclass(frozen=True)
class LostRequestMatch:
    item_id: int
    title: str
    public_description: str
    score: float
    rule_score: float
    vector_score: float | None
    matched_by: list[str]
    found_date: str
    station: str
    line: str
    storage: str
    colors: list[str]


@dataclass(frozen=True)
class LostRequestResult:
    request_id: int
    status: str
    message: str
    matches: list[LostRequestMatch]


@dataclass(frozen=True)
class ClaimCheckResult:
    request_id: int
    found_item_id: int
    status: str
    verified: bool
    message: str


class BackendClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 15.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = client

    async def list_stations(self) -> list[Station]:
        data = await self._request("GET", "/stations")
        return [
            Station(
                id=item["id"],
                name=item["name"],
                line=item["line"],
            )
            for item in data
        ]

    async def create_lost_request(
        self,
        *,
        description: str,
        lost_date: date,
        station_id: int,
    ) -> LostRequestResult:
        data = await self._request(
            "POST",
            "/lost-requests",
            json={
                "description": description,
                "lost_date": lost_date.isoformat(),
                "station_id": station_id,
            },
        )
        return LostRequestResult(
            request_id=data["request_id"],
            status=data["status"],
            message=data["message"],
            matches=[
                LostRequestMatch(
                    item_id=item["item_id"],
                    title=item["title"],
                    public_description=item["public_description"],
                    score=item["score"],
                    rule_score=item["rule_score"],
                    vector_score=item["vector_score"],
                    matched_by=item["matched_by"],
                    found_date=item["found_date"],
                    station=item["station"],
                    line=item["line"],
                    storage=item["storage"],
                    colors=item["colors"],
                )
                for item in data["matches"]
            ],
        )

    async def claim_check(
        self,
        *,
        request_id: int,
        found_item_id: int,
        answer: str,
    ) -> ClaimCheckResult:
        data = await self._request(
            "POST",
            f"/lost-requests/{request_id}/claim-check",
            json={
                "found_item_id": found_item_id,
                "answer": answer,
            },
        )
        return ClaimCheckResult(
            request_id=data["request_id"],
            found_item_id=data["found_item_id"],
            status=data["status"],
            verified=data["verified"],
            message=data["message"],
        )

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self.client is not None:
            response = await self.client.request(method, path, **kwargs)
            return self._parse_response(response)

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.request(method, path, **kwargs)
            return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = self._error_detail(response)
            raise BackendApiError(detail) from exc
        return response.json()

    def _error_detail(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return "Backend вернул некорректный ответ"

        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        return "Backend не принял заявку"
