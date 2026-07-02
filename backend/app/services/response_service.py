from app.services.matching import FoundItemMatch


class ResponseService:
    def status_for_matches(self, matches: list[FoundItemMatch]) -> str:
        if matches:
            return "claim_pending"
        return "no_matches"

    def message_for_matches(self, matches: list[FoundItemMatch]) -> str:
        if not matches:
            return "Пока совпадений нет. Заявка сохранена, ее можно будет проверить повторно позже."

        if len(matches) == 1:
            return "Мы нашли одну похожую вещь. Проверьте публичное описание и при необходимости подтвердите скрытый признак."

        return "Мы нашли несколько похожих вещей. Показываем самые вероятные варианты по описанию, дате и станции."
