class RoomRepository:

    def __init__(self):
        self.rooms = {}

    def add(self, room):
        self.rooms[room.id] = room

    def get_by_id(self, room_id):
        return self.rooms.get(room_id)