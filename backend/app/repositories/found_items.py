from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import FoundItem


class FoundItemsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_demo_items(self) -> list[FoundItem]:
        statement = (
            select(FoundItem)
            .options(
                joinedload(FoundItem.colors),
                joinedload(FoundItem.station),
                joinedload(FoundItem.storage),
            )
            .order_by(FoundItem.found_date.desc(), FoundItem.id)
        )
        return list(self.db.execute(statement).unique().scalars())

