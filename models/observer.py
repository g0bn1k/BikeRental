class Subject:
    def __init__(self):
        self._observers = []
        self.notifications = []

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, data=None):
        for observer in self._observers:
            observer.update(data)
            self.notifications.append(observer.format_notification(data))


class UserObserver:
    def update(self, data):
        # Logic to notify regular users about new bikes added
        print(f"New bike added: {data['bike_model']}")

    def format_notification(self, data):
        return f"New bike added: {data['bike_model']}"


class AdminObserver:
    def update(self, data):
        # Logic to notify admins about bike rentals
        if 'user_id' in data:
            if data['user_id'] is not None:
                print(f"Bike rented: {data['bike_model']} by user {data['user_id']}")
            else:
                print(f"Bike rented: {data['bike_model']}")

    def format_notification(self, data):
        if 'user_id' in data:
            if data['user_id'] is not None:
                return f"Bike rented: {data['bike_model']} by user {data['user_id']}"
            else:
                return f"Bike rented: {data['bike_model']}"
        else:
            return "Bike created"
