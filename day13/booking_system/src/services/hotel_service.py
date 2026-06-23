class HotelService:

    def __init__(self, hotel_repo):
        self.hotel_repo = hotel_repo

    def create_hotel(self, hotel):
        self.hotel_repo.add(hotel)