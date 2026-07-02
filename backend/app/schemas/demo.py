from datetime import date

from pydantic import BaseModel, ConfigDict


class DemoFoundItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    public_description: str
    category: str
    brand: str | None
    colors: list[str]
    found_date: date
    station: str
    line: str
    storage: str
    status: str
    has_embedding: bool
