from abc import abstractmethod, ABC

from models import Bike


class BikeDecorator(Bike, ABC):
    def __init__(self, bike):
        self.bike = bike

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def price(self):
        pass


class ChildSeat(BikeDecorator):
    def __init__(self, bike):
        super().__init__(bike)

    def description(self):
        return f"{super().description()}, Children Seat: Yes"

    def price(self):
        return self.bike.price() + 15


class GPS(BikeDecorator):
    def __init__(self, bike):
        super().__init__(bike)

    def description(self):
        return f"{super().description()}, GPS: Yes"

    def price(self):
        return self.bike.price() + 20

class RoofBag(BikeDecorator):
    def __init__(self, bike):
        super().__init__(bike)

    def description(self):
        return f"{super().description()}, Roof Bag: Yes"

    def price(self):
        return self.bike.price() + 30
