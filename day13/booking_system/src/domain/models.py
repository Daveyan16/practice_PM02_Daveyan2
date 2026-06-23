from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Hotel:
    id: Optional[int]
    name: str
    city: str


@dataclass
class Room:
    id: Optional[int]
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float


@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    package_name: str = ""
    status: BookingStatus = BookingStatus.PENDING