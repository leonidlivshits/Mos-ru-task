import asyncio
import json

import httpx

from app.services.embedding_service import OpenRouterEmbeddingService


def test_openrouter_embedding_service_sends_expected_request() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "embedding": [0.1, 0.2, 0.3],
                        "object": "embedding",
                        "index": 0,
                    }
                ],
                "model": "openai/text-embedding-3-small",
                "object": "list",
            },
        )

    async def run() -> list[list[float]] | None:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            transport=transport,
        ) as client:
            service = OpenRouterEmbeddingService(
                api_key="test-key",
                model="openai/text-embedding-3-small",
                dimensions=3,
                client=client,
            )
            return await service.embed_texts(["черный рюкзак"], input_type="search_query")

    embeddings = asyncio.run(run())

    assert embeddings == [[0.1, 0.2, 0.3]]
    assert captured["url"] == "https://openrouter.ai/api/v1/embeddings"
    assert captured["headers"]["authorization"] == "Bearer test-key"
    assert captured["payload"] == {
        "model": "openai/text-embedding-3-small",
        "input": ["черный рюкзак"],
        "dimensions": 3,
        "encoding_format": "float",
    }


def test_openrouter_embedding_service_is_disabled_without_key() -> None:
    service = OpenRouterEmbeddingService(api_key="")

    embeddings = asyncio.run(service.embed_texts(["черный рюкзак"]))

    assert embeddings is None
