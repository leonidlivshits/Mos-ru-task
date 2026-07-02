from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


class InputGuardError(ValueError):
    pass


@dataclass(frozen=True)
class InputGuard:
    min_description_length: int = 10
    max_description_length: int = 1000
    min_lost_date: date = date(2020, 1, 1)

    _control_chars_pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    _blocked_patterns = (
        re.compile(r"<\s*/?\s*script", re.IGNORECASE),
        re.compile(r"\b(drop\s+table|delete\s+from|insert\s+into|update\s+\w+\s+set)\b", re.IGNORECASE),
        re.compile(r"(--|/\*|\*/)", re.IGNORECASE),
    )

    def clean_description(self, description: str) -> str:
        if self._control_chars_pattern.search(description):
            raise InputGuardError("Описание содержит недопустимые символы")

        cleaned = " ".join(description.split())

        if len(cleaned) < self.min_description_length:
            raise InputGuardError("Описание слишком короткое, добавьте тип вещи, цвет или особые признаки")

        if len(cleaned) > self.max_description_length:
            raise InputGuardError("Описание слишком длинное")

        if any(pattern.search(cleaned) for pattern in self._blocked_patterns):
            raise InputGuardError("Описание содержит потенциально небезопасный ввод")

        return cleaned

    def validate_lost_date(self, lost_date: date) -> None:
        if lost_date > date.today():
            raise InputGuardError("Дата потери не может быть в будущем")

        if lost_date < self.min_lost_date:
            raise InputGuardError("Дата потери слишком старая для демостенда")
