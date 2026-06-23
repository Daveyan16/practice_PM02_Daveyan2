from pydantic import BaseModel


class HotelCreateDTO(BaseModel):
    name: str
    city: str