class User:
    def __init__(self, user_id: int, email: str, phone: str):
        self.id = user_id
        self.email = email
        self.phone = phone

class Booking:
    def __init__(self, booking_id: int, user_id: int):
        self.id = booking_id
        self.user_id = user_id