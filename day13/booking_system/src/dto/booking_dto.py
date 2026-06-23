from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List


class BookingCreateDTO(BaseModel):
    """DTO для создания бронирования"""
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    service_ids: List[int] = []

    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if (v - values['check_in']).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v


class BookingResponseDTO(BaseModel):
    """DTO для ответа с данными о бронировании"""
    id: int
    room_id: int
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime
    service_ids: List[int] = []
    service_names: List[str] = []

    class Config:
        from_attributes = True


class BookingUpdateDTO(BaseModel):
    """DTO для обновления бронирования"""
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    service_ids: Optional[List[int]] = None