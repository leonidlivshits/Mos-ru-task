from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedRequest:
    description: str
    tokens: list[str]
    category: str | None
    colors: list[str]
    brand: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "description": self.description,
            "tokens": self.tokens,
            "category": self.category,
            "colors": self.colors,
            "brand": self.brand,
        }


def normalize_text(value: str) -> str:
    return value.lower().replace("ё", "е")


def tokenize(value: str) -> list[str]:
    return re.findall(r"[a-zа-я0-9&]+", normalize_text(value))


class NormalizationService:
    category_keywords: dict[str, tuple[str, ...]] = {
        "рюкзак": ("рюкзак", "рюкзака", "рюкзаком", "backpack", "ryukzak"),
        "сумка": ("сумка", "сумку", "сумки", "bag", "sumka"),
        "пакет": ("пакет", "пакета", "мешок", "package", "paket"),
        "кошелек": ("кошелек", "кошелек", "кошелька", "wallet", "koshelek"),
        "куртка": ("куртка", "куртку", "куртки", "jacket", "kurtka"),
        "мяч": ("мяч", "мяча", "мячик", "футбольный мяч", "ball"),
        "телефон": ("телефон", "смартфон", "phone", "samsung", "iphone"),
        "наушники": ("наушники", "airpods", "earbuds", "headphones"),
        "зонт": ("зонт", "зонтик", "umbrella", "zont"),
        "документы": ("документы", "папка", "договор", "documents"),
        "ноутбук": ("ноутбук", "laptop", "lenovo"),
        "косметичка": ("косметичка", "cosmetic"),
    }
    color_keywords: dict[str, tuple[str, ...]] = {
        "черный": ("черный", "черная", "черное", "черные", "черно", "black", "chernyi"),
        "синий": ("синий", "синяя", "синее", "синие", "сине", "blue", "siniy", "siney"),
        "серый": ("серый", "серая", "серое", "серые", "grey", "gray", "seryi"),
        "зеленый": ("зеленый", "зеленая", "зеленое", "зеленые", "green", "zelenyi"),
        "красный": ("красный", "красная", "красное", "красные", "red", "krasnyi"),
        "белый": ("белый", "белая", "белое", "белые", "white", "belyi"),
        "желтый": ("желтый", "желтая", "желтое", "желтые", "yellow", "zheltyi"),
        "розовый": ("розовый", "розовая", "розовое", "розовые", "pink", "rozovyi"),
        "коричневый": ("коричневый", "коричневая", "brown", "korichnevyi"),
        "голубой": ("голубой", "голубая", "lightblue", "goluboy"),
    }
    brands: tuple[str, ...] = (
        "Nike",
        "Adidas",
        "Puma",
        "Samsung",
        "Apple",
        "Lenovo",
        "Xiaomi",
        "H&M",
        "Swissgear",
        "Daigisi",
        "Poppin",
    )

    def normalize(self, description: str) -> NormalizedRequest:
        normalized_description = normalize_text(description)
        tokens = tokenize(description)
        token_set = set(tokens)

        category = self._first_match(self.category_keywords, normalized_description, token_set)
        colors = [
            color
            for color, keywords in self.color_keywords.items()
            if self._contains_keyword(normalized_description, token_set, keywords)
        ]
        brand = self._extract_brand(normalized_description)

        return NormalizedRequest(
            description=normalized_description,
            tokens=tokens,
            category=category,
            colors=colors,
            brand=brand,
        )

    def _first_match(
        self,
        keywords_by_value: dict[str, tuple[str, ...]],
        normalized_description: str,
        token_set: set[str],
    ) -> str | None:
        for value, keywords in keywords_by_value.items():
            if self._contains_keyword(normalized_description, token_set, keywords):
                return value
        return None

    def _extract_brand(self, normalized_description: str) -> str | None:
        for brand in self.brands:
            if normalize_text(brand) in normalized_description:
                return brand
        return None

    def _contains_keyword(
        self,
        normalized_description: str,
        token_set: set[str],
        keywords: tuple[str, ...],
    ) -> bool:
        return any(normalize_text(keyword) in token_set or normalize_text(keyword) in normalized_description for keyword in keywords)
