from html import escape

from app.telegram_bot.backend_client import LostRequestResult


def format_lost_request_result(result: LostRequestResult) -> str:
    lines = [
        f"<b>Заявка #{result.request_id}</b>",
        escape(result.message),
    ]

    if not result.matches:
        return "\n".join(lines)

    lines.append("")
    lines.append("<b>Похожие вещи:</b>")

    for index, match in enumerate(result.matches, start=1):
        score_line = f"score {match.score:.2f}, rules {match.rule_score:.2f}"
        if match.vector_score is not None:
            score_line += f", vector {match.vector_score:.2f}"

        lines.extend(
            [
                "",
                f"<b>{index}. {escape(match.title)}</b>",
                escape(match.public_description),
                f"Станция: {escape(match.station)} ({escape(match.line)})",
                f"Дата находки: {escape(match.found_date)}",
                f"Цвета: {escape(', '.join(match.colors)) if match.colors else 'не указаны'}",
                f"Почему подходит: {escape(', '.join(match.matched_by))}",
                score_line,
            ]
        )

    lines.append("")
    lines.append("Для подтверждения в реальном сервисе нужно будет назвать скрытый признак вещи.")
    return "\n".join(lines)
