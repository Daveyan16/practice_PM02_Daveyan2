from pydantic import BaseModel


class RoomCreateDTO(BaseModel):
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float