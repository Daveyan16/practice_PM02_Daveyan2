class HotelRepository:

    def __init__(self):
        self.hotels = {}

    def add(self, hotel):
        self.hotels[hotel.id] = hotel

    def get_by_id(self, hotel_id):
        return self.hotels.get(hotel_id)