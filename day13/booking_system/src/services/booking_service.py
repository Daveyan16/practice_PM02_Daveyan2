class BookingService:

    def __init__(
        self,
        booking_repo,
        room_repo,
        pricing_service
    ):
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.pricing_service = pricing_service

    def create_booking(self, dto):
        room = self.room_repo.get_by_id(
            dto.room_id
        )

        return self.pricing_service.calculate_price(
            room,
            dto.check_in,
            dto.check_out
        )