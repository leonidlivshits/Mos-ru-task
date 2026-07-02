from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy import text

from app.db.models import (
    Color,
    FoundItem,
    MetroStation,
    StorageLocation,
)
from app.db.session import SessionLocal


STATIONS = [
    {"name": "Новохохловская", "line": "МЦК", "nearby_stations": ["Нижегородская"], "interchange_nodes": []},
    {"name": "Соколиная гора", "line": "МЦК", "nearby_stations": ["Шоссе Энтузиастов"], "interchange_nodes": []},
    {"name": "Балтийская", "line": "МЦК", "nearby_stations": ["Стрешнево"], "interchange_nodes": []},
    {"name": "Стрешнево", "line": "МЦК", "nearby_stations": ["Балтийская"], "interchange_nodes": []},
    {"name": "Театральная", "line": "Замоскворецкая", "nearby_stations": ["Тверская"], "interchange_nodes": ["Охотный Ряд", "Площадь Революции"]},
    {"name": "Арбатская", "line": "Арбатско-Покровская", "nearby_stations": ["Смоленская"], "interchange_nodes": ["Библиотека имени Ленина"]},
    {"name": "Тверская", "line": "Замоскворецкая", "nearby_stations": ["Театральная", "Маяковская"], "interchange_nodes": ["Пушкинская", "Чеховская"]},
    {"name": "Пушкинская", "line": "Таганско-Краснопресненская", "nearby_stations": ["Кузнецкий Мост"], "interchange_nodes": ["Тверская", "Чеховская"]},
]

COLORS = [
    "черный",
    "синий",
    "серый",
    "зеленый",
    "красный",
    "белый",
    "желтый",
    "розовый",
    "коричневый",
    "голубой",
]

STORAGES = [
    {"name": "Склад забытых вещей", "address": "Москва, склад демонстрационных находок"},
    {"name": "Дежурный по станции", "address": "Хранение на станции до передачи на склад"},
    {"name": "Бюро находок метрополитена", "address": "Демонстрационный пункт выдачи"},
]

FOUND_ITEMS = [
    {
        "title": "Черно-синий рюкзак Swissgear",
        "description": "Рюкзак черно-синего цвета Swissgear, внутри вилка, рабочие перчатки, канцелярский нож и зеленый дождевик.",
        "public_description": "Черно-синий рюкзак, найден в вагоне.",
        "private_features": ["вилка", "рабочие перчатки", "зеленый дождевик"],
        "category": "рюкзак",
        "brand": "Swissgear",
        "found_date": date(2026, 6, 28),
        "station": "Новохохловская",
        "storage": "Склад забытых вещей",
        "colors": ["черный", "синий"],
    },
    {
        "title": "Пакет с одеждой",
        "description": "Пакет белого цвета с газетным принтом, внутри красные брюки, серая кофта и кофта с разноцветными бабочками.",
        "public_description": "Белый пакет с одеждой, найден в вагоне.",
        "private_features": ["красные брюки", "серая кофта", "принт бабочки"],
        "category": "пакет",
        "brand": None,
        "found_date": date(2026, 6, 27),
        "station": "Новохохловская",
        "storage": "Склад забытых вещей",
        "colors": ["белый", "красный", "серый"],
    },
    {
        "title": "Пакет с лекарствами",
        "description": "Белый пакет, внутри таблетки Мирапекс и сигареты.",
        "public_description": "Белый пакет, найден в вагоне.",
        "private_features": ["Мирапекс", "сигареты"],
        "category": "пакет",
        "brand": None,
        "found_date": date(2026, 6, 29),
        "station": "Новохохловская",
        "storage": "Бюро находок метрополитена",
        "colors": ["белый"],
    },
    {
        "title": "Спортивная сумка Nike",
        "description": "Дорожная спортивная сумка черного цвета Nike, внутри черное пальто Puma, красный жилет и серые джинсы.",
        "public_description": "Черная спортивная сумка Nike, найдена в вагоне.",
        "private_features": ["пальто Puma", "красный жилет", "серые джинсы"],
        "category": "сумка",
        "brand": "Nike",
        "found_date": date(2026, 6, 28),
        "station": "Новохохловская",
        "storage": "Склад забытых вещей",
        "colors": ["черный", "красный", "серый"],
    },
    {
        "title": "Двухсторонняя куртка",
        "description": "Куртка черная с желтым градиентом, в кармане связка ключей и брелок матрешка.",
        "public_description": "Черно-желтая куртка, найдена в вагоне.",
        "private_features": ["связка ключей", "брелок матрешка"],
        "category": "куртка",
        "brand": None,
        "found_date": date(2026, 6, 29),
        "station": "Новохохловская",
        "storage": "Дежурный по станции",
        "colors": ["черный", "желтый"],
    },
    {
        "title": "Зеленый пакет с одеждой",
        "description": "Пакет зеленого цвета, внутри тапки сиреневые, толстовка серо-синяя с капюшоном и синие джинсы.",
        "public_description": "Зеленый пакет с одеждой, найден в вагоне.",
        "private_features": ["сиреневые тапки", "серо-синяя толстовка", "синие джинсы"],
        "category": "пакет",
        "brand": None,
        "found_date": date(2026, 6, 30),
        "station": "Соколиная гора",
        "storage": "Склад забытых вещей",
        "colors": ["зеленый", "синий", "серый"],
    },
    {
        "title": "Рюкзак H&M",
        "description": "Рюкзак черно-серого цвета с белыми разводами, внутри розовая толстовка H&M.",
        "public_description": "Черно-серый рюкзак, найден в вагоне.",
        "private_features": ["розовая толстовка H&M", "белые разводы на ткани"],
        "category": "рюкзак",
        "brand": "H&M",
        "found_date": date(2026, 6, 28),
        "station": "Балтийская",
        "storage": "Склад забытых вещей",
        "colors": ["черный", "серый", "белый", "розовый"],
    },
    {
        "title": "Черный кошелек Daigisi",
        "description": "Кошелек черного цвета с желтой надписью Daigisi, внутри 400 рублей и карта Тройка.",
        "public_description": "Черный кошелек, найден на станции.",
        "private_features": ["400 рублей", "карта Тройка", "желтая надпись Daigisi"],
        "category": "кошелек",
        "brand": "Daigisi",
        "found_date": date(2026, 6, 29),
        "station": "Стрешнево",
        "storage": "Дежурный по станции",
        "colors": ["черный", "желтый"],
    },
    {
        "title": "Серый рюкзак Poppin",
        "description": "Рюкзак серого цвета Poppin, внутри бейсболка Burger King, сине-черная шапка Adidas и темно-серая водолазка.",
        "public_description": "Серый рюкзак, найден в вагоне.",
        "private_features": ["бейсболка Burger King", "шапка Adidas", "темно-серая водолазка"],
        "category": "рюкзак",
        "brand": "Poppin",
        "found_date": date(2026, 6, 30),
        "station": "Театральная",
        "storage": "Склад забытых вещей",
        "colors": ["серый", "синий", "черный"],
    },
    {
        "title": "Пакет Adidas",
        "description": "Пакет с черной майкой и красным спортивным костюмом Adidas.",
        "public_description": "Пакет со спортивной одеждой, найден в вагоне.",
        "private_features": ["черная майка", "красный спортивный костюм"],
        "category": "пакет",
        "brand": "Adidas",
        "found_date": date(2026, 6, 29),
        "station": "Арбатская",
        "storage": "Бюро находок метрополитена",
        "colors": ["черный", "красный"],
    },
    {
        "title": "Черный телефон Samsung",
        "description": "Черный телефон Samsung в синем чехле, на чехле маленькая наклейка со звездой.",
        "public_description": "Черный телефон Samsung, найден на станции.",
        "private_features": ["синий чехол", "наклейка со звездой"],
        "category": "телефон",
        "brand": "Samsung",
        "found_date": date(2026, 6, 30),
        "station": "Тверская",
        "storage": "Дежурный по станции",
        "colors": ["черный", "синий"],
    },
    {
        "title": "Белые наушники Apple",
        "description": "Белые беспроводные наушники Apple в кейсе, на кейсе небольшая царапина сбоку.",
        "public_description": "Белые беспроводные наушники, найдены в вагоне.",
        "private_features": ["царапина на кейсе"],
        "category": "наушники",
        "brand": "Apple",
        "found_date": date(2026, 6, 30),
        "station": "Пушкинская",
        "storage": "Склад забытых вещей",
        "colors": ["белый"],
    },
    {
        "title": "Синий зонт",
        "description": "Складной зонт синего цвета с черной ручкой и потертостью на чехле.",
        "public_description": "Синий складной зонт, найден на станции.",
        "private_features": ["черная ручка", "потертость на чехле"],
        "category": "зонт",
        "brand": None,
        "found_date": date(2026, 6, 28),
        "station": "Тверская",
        "storage": "Дежурный по станции",
        "colors": ["синий", "черный"],
    },
    {
        "title": "Коричневый кошелек",
        "description": "Коричневый кожаный кошелек, внутри студенческий билет и карта банка.",
        "public_description": "Коричневый кошелек, найден в вагоне.",
        "private_features": ["студенческий билет", "банковская карта"],
        "category": "кошелек",
        "brand": None,
        "found_date": date(2026, 6, 27),
        "station": "Арбатская",
        "storage": "Бюро находок метрополитена",
        "colors": ["коричневый"],
    },
    {
        "title": "Голубая папка с документами",
        "description": "Голубая пластиковая папка с распечатками и копией договора.",
        "public_description": "Голубая папка с документами, найдена на станции.",
        "private_features": ["копия договора", "распечатки"],
        "category": "документы",
        "brand": None,
        "found_date": date(2026, 6, 29),
        "station": "Театральная",
        "storage": "Бюро находок метрополитена",
        "colors": ["голубой"],
    },
    {
        "title": "Черно-белый рюкзак Xiaomi",
        "description": "Черно-белый рюкзак Xiaomi, внутри зарядное устройство, блокнот и зеленая бутылка.",
        "public_description": "Черно-белый рюкзак, найден в вагоне.",
        "private_features": ["зарядное устройство", "зеленая бутылка", "блокнот"],
        "category": "рюкзак",
        "brand": "Xiaomi",
        "found_date": date(2026, 6, 30),
        "station": "Пушкинская",
        "storage": "Склад забытых вещей",
        "colors": ["черный", "белый", "зеленый"],
    },
    {
        "title": "Красная сумка Puma",
        "description": "Красная сумка Puma, внутри серые кроссовки и полотенце.",
        "public_description": "Красная спортивная сумка, найдена на станции.",
        "private_features": ["серые кроссовки", "полотенце"],
        "category": "сумка",
        "brand": "Puma",
        "found_date": date(2026, 6, 28),
        "station": "Балтийская",
        "storage": "Дежурный по станции",
        "colors": ["красный", "серый"],
    },
    {
        "title": "Серый ноутбук Lenovo",
        "description": "Серый ноутбук Lenovo в черном чехле, внутри наклейка с именем владельца.",
        "public_description": "Серый ноутбук Lenovo, найден в вагоне.",
        "private_features": ["черный чехол", "наклейка с именем"],
        "category": "ноутбук",
        "brand": "Lenovo",
        "found_date": date(2026, 6, 29),
        "station": "Новохохловская",
        "storage": "Бюро находок метрополитена",
        "colors": ["серый", "черный"],
    },
    {
        "title": "Желтый детский рюкзак",
        "description": "Желтый детский рюкзак с красной машинкой, внутри пенал и игрушка.",
        "public_description": "Желтый детский рюкзак, найден на станции.",
        "private_features": ["пенал", "игрушка", "рисунок машинки"],
        "category": "рюкзак",
        "brand": None,
        "found_date": date(2026, 6, 27),
        "station": "Соколиная гора",
        "storage": "Склад забытых вещей",
        "colors": ["желтый", "красный"],
    },
    {
        "title": "Розовая косметичка",
        "description": "Розовая косметичка без бренда, внутри помада, зеркало и ключ.",
        "public_description": "Розовая косметичка, найдена в вагоне.",
        "private_features": ["помада", "зеркало", "ключ"],
        "category": "косметичка",
        "brand": None,
        "found_date": date(2026, 6, 30),
        "station": "Тверская",
        "storage": "Склад забытых вещей",
        "colors": ["розовый"],
    },
]


async def seed() -> None:
    async with SessionLocal() as db:
        await db.execute(
            text(
                """
                TRUNCATE TABLE
                    request_matches,
                    lost_requests,
                    found_item_colors,
                    found_items,
                    colors,
                    metro_stations,
                    storage_locations
                RESTART IDENTITY CASCADE
                """
            )
        )
        await db.commit()

        stations = {
            data["name"]: MetroStation(**data)
            for data in STATIONS
        }
        colors = {name: Color(name=name) for name in COLORS}
        storages = {
            data["name"]: StorageLocation(**data)
            for data in STORAGES
        }
        db.add_all([*stations.values(), *colors.values(), *storages.values()])
        await db.flush()

        for data in FOUND_ITEMS:
            item_data = data.copy()
            item_colors = [colors[color_name] for color_name in item_data.pop("colors")]
            station = stations[item_data.pop("station")]
            storage = storages[item_data.pop("storage")]
            item = FoundItem(
                **item_data,
                station=station,
                storage=storage,
                colors=item_colors,
            )
            db.add(item)

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print(f"Seeded demo database with {len(FOUND_ITEMS)} found items.")
