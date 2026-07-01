from html import escape


START_MESSAGE = (
    "Привет. Я демо-бот для поиска потерянных вещей в метро.\n\n"
    "Опишите потерянную вещь: тип, цвет, бренд и особые признаки. "
    "Например: черный рюкзак Nike, внутри синяя папка."
)

CANCEL_MESSAGE = "Заявка сброшена. Чтобы начать заново, отправьте /start."
DESCRIPTION_REQUIRED_MESSAGE = "Отправьте описание текстом."

LOST_DATE_PROMPT = (
    "Теперь укажите дату потери.\n"
    "Формат: 2026-06-30 или 30.06.2026."
)
LOST_DATE_REQUIRED_MESSAGE = "Отправьте дату текстом."
INVALID_LOST_DATE_MESSAGE = "Не понял дату. Используйте формат 2026-06-30 или 30.06.2026."

BACKEND_UNAVAILABLE_MESSAGE = "Backend сейчас недоступен. Попробуйте еще раз чуть позже."
STATION_PROMPT = "Выберите станцию, где вещь была потеряна."
DAMAGED_DATE_MESSAGE = "Дата в заявке повреждена. Начните заново через /start."

CLAIM_FEATURE_REQUIRED_MESSAGE = "Отправьте скрытый признак текстом."
FALLBACK_MESSAGE = "Чтобы начать демо-сценарий, отправьте /start."


def create_request_error_message(error: object) -> str:
    return f"Не удалось создать заявку: {error}\nНачните заново через /start."


def claim_check_error_message(error: object) -> str:
    return f"Не удалось проверить признак: {error}\nНачните заново через /start."


def claim_feature_prompt(item_title: str) -> str:
    return (
        "Для демо проверим самый вероятный вариант.\n"
        f"Напишите скрытый признак вещи: что было внутри или какая особая примета у «{escape(item_title)}»?"
    )
