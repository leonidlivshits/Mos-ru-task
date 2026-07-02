from __future__ import annotations

import asyncio

from app.db.models import FoundItem
from app.db.session import SessionLocal
from app.repositories.found_items import FoundItemsRepository
from app.services.embedding_service import EmbeddingServiceError, OpenRouterEmbeddingService


def embedding_text(item: FoundItem) -> str:
    return f"{item.title}. {item.public_description}. {item.description}"


def chunks(items: list[FoundItem], size: int) -> list[list[FoundItem]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


async def fill_embeddings(batch_size: int = 10) -> None:
    embedding_service = OpenRouterEmbeddingService()
    if not embedding_service.is_configured:
        print("OPENROUTER_API_KEY is empty. Add it to .env and run the script again.")
        return

    async with SessionLocal() as db:
        found_items = FoundItemsRepository(db)
        items = await found_items.list_without_embeddings()
        if not items:
            print("All found items already have embeddings.")
            return

        updated = 0
        for batch in chunks(items, batch_size):
            texts = [embedding_text(item) for item in batch]
            embeddings = await embedding_service.embed_texts(texts, input_type="search_document")
            if embeddings is None:
                print("Embeddings are disabled.")
                return

            await found_items.update_embeddings(batch, embeddings)
            updated += len(batch)

        print(f"Filled description_embedding for {updated} found items.")


if __name__ == "__main__":
    try:
        asyncio.run(fill_embeddings())
    except EmbeddingServiceError as exc:
        raise SystemExit(str(exc)) from exc
