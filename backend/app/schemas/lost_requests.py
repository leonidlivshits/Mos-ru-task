from datetime import date

from pydantic import BaseModel, Field


class LostRequestCreate(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    lost_date: date
    station_id: int = Field(gt=0)


class LostRequestCreated(BaseModel):
    request_id: int
    status: str
