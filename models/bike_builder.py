# models/factories.py
from abc import abstractmethod, ABC

from db_models import Bikes


class Factory(ABC):
    @abstractmethod
    def create(self, name, model, year, color, price, image_url):
        pass


class BikeFactory(Factory):
    def create(self, name, model, year, color, price, image_url):
        if not all([name, model, year, color, price, image_url]):
            raise ValueError("Incomplete bike information. Make sure all attributes are set.")

        # Create and return a new Bikes object
        return Bikes(
            name=name,
            model=model,
            year=year,
            color=color,
            price=price,
            image_url=image_url
        )


