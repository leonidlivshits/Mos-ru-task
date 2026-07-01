import asyncio
import json
from datetime import date

import httpx

from app.telegram_bot.backend_client import BackendApiError, BackendClient, LostRequestMatch, LostRequestResult
from app.telegram_bot.dates import parse_lost_date
from app.telegram_bot.formatting import format_lost_request_result


def test_parse_lost_date_supports_iso_and_ru_formats() -> None:
    assert parse_lost_date("2026-06-30") == date(2026, 6, 30)
    assert parse_lost_date("30.06.2026") == date(2026, 6, 30)
    assert parse_lost_date("30/06/2026") is None


def test_format_lost_request_result_escapes_html() -> None:
    result = LostRequestResult(
        request_id=1,
        status="matched",
        message="Нашли <вариант>",
        matches=[
            LostRequestMatch(
                item_id=12,
                title="Черный <рюкзак>",
                public_description="Найден & сохранен",
                score=0.87,
                rule_score=0.8,
                vector_score=0.9,
                matched_by=["semantic", "цвет"],
                found_date="2026-06-30",
                station="Тверская",
                line="Замоскворецкая",
                storage="Склад",
                colors=["черный"],
            )
        ],
    )

    text = format_lost_request_result(result)

    assert "&lt;вариант&gt;" in text
    assert "Черный &lt;рюкзак&gt;" in text
    assert "vector 0.90" in text


def test_backend_client_creates_lost_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "http://backend/lost-requests"
        assert json.loads(request.content.decode()) == {
            "description": "черный рюкзак",
            "lost_date": "2026-06-30",
            "station_id": 1,
        }
        return httpx.Response(
            201,
            json={
                "request_id": 7,
                "status": "matched",
                "message": "Нашли похожие вещи",
                "matches": [],
            },
        )

    async def run() -> None:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="http://backend", transport=transport) as http_client:
            client = BackendClient("http://backend", client=http_client)
            result = await client.create_lost_request(
                description="черный рюкзак",
                lost_date=date(2026, 6, 30),
                station_id=1,
            )

        assert result.request_id == 7
        assert result.status == "matched"

    asyncio.run(run())


def test_backend_client_raises_readable_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Станция не найдена"})

    async def run() -> None:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="http://backend", transport=transport) as http_client:
            client = BackendClient("http://backend", client=http_client)
            try:
                await client.list_stations()
            except BackendApiError as exc:
                assert str(exc) == "Станция не найдена"
            else:
                raise AssertionError("BackendApiError was not raised")

    asyncio.run(run())
