from abc import ABC, abstractmethod

from db_models import Rentals


class Builder(ABC):
    @abstractmethod
    def build(self):
        pass


class RentalsBuilder(Builder):
    def __init__(self, rentals=None):
        self.rentals = rentals if rentals else Rentals()
        self.decorations = []

    def set_user_id(self, user_id):
        self.rentals.user_id = user_id
        return self

    def set_bike_id(self, bike_id):
        self.rentals.bike_id = bike_id
        return self

    def set_bike_model(self, bike_model):
        self.rentals.bike_model = bike_model
        return self

    def set_bike_name(self, bike_name):
        self.rentals.bike_name = bike_name
        return self

    def add_decoration(self, decoration):
        self.decorations.append(decoration)
        return self

    def set_start_date(self, start_date):
        self.rentals.start_date = start_date
        return self

    def set_end_date(self, end_date):
        self.rentals.end_date = end_date
        return self

    def set_price_per_day(self, price_per_day):
        self.rentals.price_per_day = price_per_day
        return self

    def set_rental_days(self, rental_days):
        self.rentals.rental_days = rental_days
        return self

    def calculate_total_price(self):
        if self.rentals.price_per_day is None or self.rentals.rental_days is None:
            raise ValueError("Price per day and rental days must be set before calculating total price")
        self.rentals.total_price = self.rentals.price_per_day * self.rentals.rental_days
        return self

    @property
    def build(self):
        if not all([self.rentals.user_id, self.rentals.bike_id, self.rentals.start_date, self.rentals.end_date,
                    self.rentals.price_per_day, self.rentals.total_price, self.rentals.rental_days]):
            raise ValueError("All parameters must be set before building Rentals")

        new_rentals = Rentals(
            user_id=self.rentals.user_id

        )

        return self.rentals
