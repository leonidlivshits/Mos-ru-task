from datetime import date, datetime


SUPPORTED_DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y")


def parse_lost_date(value: str) -> date | None:
    for date_format in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    return None
