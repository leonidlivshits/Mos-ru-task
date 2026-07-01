from pydantic import BaseModel, ConfigDict


class StationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    line: str
    nearby_stations: list[str]
    interchange_nodes: list[str]
