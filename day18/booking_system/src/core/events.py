from dataclasses import dataclass

@dataclass
class BookingCreatedEvent:
    booking_id: int

@dataclass
class PaymentFailedEvent:
    booking_id: int