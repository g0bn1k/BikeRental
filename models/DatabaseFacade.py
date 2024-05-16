from sqlalchemy import select
from db import DatabaseConnector, db
from db_models import User, Bikes, Rentals


class DatabaseFacade:
    def __init__(self):
        self.connector = DatabaseConnector()

    def fetch_all_bikes(self):
        bikes_query = select(Bikes).filter()
        bikes = db.session.execute(bikes_query).scalars().all()
        return bikes

    def fetch_bike_by_id(self,bike_id):
        bike = db.session.query(Bikes).get(bike_id)
        return bike


    def fetch_all_available_bikes(self):
        bikes_query = select(Bikes).filter(Bikes.state == 'available')
        bikes = db.session.execute(bikes_query).scalars().all()
        return bikes

    def fetch_all_users(self):
        return db.session.query(User).all()

    def add_user(self, username, email, password, full_name):
        user = User(username=username, email=email, password=password, full_name=full_name)
        self.connector.db.session.add(user)
        self.connector.db.session.commit()

        return user

    def fetch_user_rented_bikes(self, user_id):
        rented_bikes = db.session.query(Rentals).filter_by(user_id=user_id).all()
        return rented_bikes

    def fetch_all_rented_bikes(self):
        rented_bikes = db.session.query(Rentals).all()
        return rented_bikes

    def delete_bike(self, bike_id):
        bike = db.session.query(Bikes).get(bike_id)
        if bike:
            db.session.delete(bike)
            db.session.commit()

    def delete_rental(self, rental_id):
        rental = db.session.query(Rentals).get(rental_id)
        if rental:
            bike_id = rental.bike_id

            # Update the status of the bike to 'available'
            bike = db.session.query(Bikes).get(bike_id)
            if bike:
                bike.state = 'available'
                db.session.commit()
            else:
                print(f"Bike {bike_id} not found")

            # Delete the rental after updating the bike state
            db.session.delete(rental)
            db.session.commit()

    def delete_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def fetch_rental_by_id(self, rental_id):
        rental = db.session.query(Rentals).get(rental_id)
        return rental

    def delete_bike_by_id(self, bike_id):
        bike = db.session.query(Bikes).get(bike_id)
        if bike:
            db.session.delete(bike)
            db.session.commit()

    def fetch_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        return user
