from datetime import date

from pydantic import BaseModel, Field


class LostRequestCreate(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    lost_date: date
    station_id: int = Field(gt=0)


class LostRequestMatch(BaseModel):
    item_id: int
    title: str
    public_description: str
    score: float
    rule_score: float
    vector_score: float | None
    matched_by: list[str]
    found_date: date
    station: str
    line: str
    storage: str
    colors: list[str]


class LostRequestCreated(BaseModel):
    request_id: int
    status: str
    message: str
    matches: list[LostRequestMatch]
