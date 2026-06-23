class DomainError(Exception):
    pass


class HotelNotFoundError(DomainError):
    pass


class RoomNotFoundError(DomainError):
    pass


class BookingConflictError(DomainError):
    pass