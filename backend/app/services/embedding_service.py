from __future__ import annotations

import httpx

from app.core.config import settings


class EmbeddingServiceError(RuntimeError):
    pass


class OpenRouterEmbeddingService:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
        http_referer: str | None = None,
        app_title: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = settings.openrouter_api_key if api_key is None else api_key
        self.base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self.model = model or settings.openrouter_embedding_model
        self.dimensions = dimensions or settings.openrouter_embedding_dimensions
        self.http_referer = http_referer or settings.openrouter_http_referer
        self.app_title = app_title or settings.openrouter_app_title
        self.client = client

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def embed_text(self, text: str, *, input_type: str | None = None) -> list[float] | None:
        embeddings = await self.embed_texts([text], input_type=input_type)
        if not embeddings:
            return None
        return embeddings[0]

    async def embed_texts(self, texts: list[str], *, input_type: str | None = None) -> list[list[float]] | None:
        if not texts or not self.is_configured:
            return None

        _ = input_type
        payload: dict[str, object] = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
            "encoding_format": "float",
        }

        try:
            response = await self._post_embeddings(payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingServiceError("Не удалось получить embeddings от OpenRouter") from exc

        data = response.json()
        embeddings = [item["embedding"] for item in data.get("data", [])]
        if len(embeddings) != len(texts):
            raise EmbeddingServiceError("OpenRouter вернул некорректное количество embeddings")

        for embedding in embeddings:
            if len(embedding) != self.dimensions:
                raise EmbeddingServiceError("Размер embedding не совпадает с настройкой pgvector")

        return embeddings

    async def _post_embeddings(self, payload: dict[str, object]) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.http_referer,
            "X-OpenRouter-Title": self.app_title,
        }
        if self.client is not None:
            return await self.client.post("/embeddings", headers=headers, json=payload)

        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            return await client.post("/embeddings", headers=headers, json=payload)
