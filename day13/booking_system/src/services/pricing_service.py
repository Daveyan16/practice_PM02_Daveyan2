from abc import ABC, abstractmethod


class ServiceComponent(ABC):

    @abstractmethod
    def get_price(self):
        pass


class Breakfast(ServiceComponent):

    def get_price(self):
        return 15


class Transfer(ServiceComponent):

    def get_price(self):
        return 30


class ServicePackage(ServiceComponent):

    def __init__(self, name):
        self.name = name
        self.services = []

    def add(self, service):
        self.services.append(service)

    def get_price(self):
        return sum(
            service.get_price()
            for service in self.services
        )


class PricingService:

    def calculate_price(
        self,
        room,
        check_in,
        check_out,
        package=None
    ):

        nights = (
            check_out - check_in
        ).days

        room_price = (
            nights *
            room.price_per_night
        )

        package_price = (
            package.get_price()
            if package
            else 0
        )

        return room_price + package_price