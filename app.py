import os
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor for parallel processing
from datetime import datetime
from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash, session
from werkzeug.utils import secure_filename
from db import db
from db_models import Bikes, User, Rentals, Base
from models.DatabaseFacade import DatabaseFacade
from models.RentalStrategy import StandardPricingStrategy, MonthlyPricingStrategy
from models.Reposotory import UserRepository
from models.bike_builder import BikeFactory
from models.bike_decorator import *
from models.observer import Subject, AdminObserver, UserObserver

# Import statements

# Initialize the Flask app
app = Flask(__name__)

# Define constants
UPLOAD_FOLDER = 'photos'

# Configure the Flask app
app.config['SECRET_KEY'] = 'do later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/bikerentaldb'
app.config['UPLOADED_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
db.init_app(app)
db.migrate(app, Base)

# Initialize the DatabaseFacade instance
db_facade = DatabaseFacade()

# Register the admin observer

subject = Subject()
subject.register(AdminObserver())
subject.register(UserObserver())

# Initialize the ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)

bike_factory = BikeFactory()


@app.route('/')
def main():
    # Fetch all bikes using DatabaseFacade
    bikes = db_facade.fetch_all_available_bikes()
    user_logged_in = 'user_id' in session
    return render_template('home.html', bikes=bikes, user_logged_in=user_logged_in, title="Bike Rental")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']

        new_user = db_facade.add_user(username, email, password, full_name)

        flash("User registered successfully", "success")
        return redirect(url_for('login'))

    return render_template('register.html', title="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use db.session.query() instead of User.query
        login_user = db.session.query(User).filter_by(username=username, password=password).first()

        if login_user is not None:
            login_user.last_login = datetime.now()  # Update last login time
            db.session.commit()

            # Set user_id in session upon successful login
            session['user_id'] = login_user.id_user

            return redirect(url_for('account'))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route('/delete-user/<int:id_user>', methods=['GET', 'POST'])
def delete_user(id_user):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Call the delete_user method from UserRepository
        if UserRepository.delete_user(id_user):
            flash("User deleted successfully", "success")
        else:
            flash("User not found", "error")

        return redirect(url_for('home'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db_facade.fetch_user_by_id(user_id)
    user_logged_in = True
    username = user.username
    notifications = subject.notifications

    if user.is_admin:
        all_users = db_facade.fetch_all_users()
        all_rented_bikes = db_facade.fetch_all_rented_bikes()
        bikes = db_facade.fetch_all_bikes()

        return render_template('account.html', rented_bikes=all_rented_bikes, is_admin=user.is_admin,
                               user_logged_in=user_logged_in,
                               all_users=all_users, username=username, bikes=bikes, notifications=notifications)
    else:
        return render_template('account.html', is_admin=user.is_admin,
                               user_logged_in=user_logged_in, username=username, notifications=notifications)


@app.route('/rented-bikes')
def rented_bikes():
    if 'user_id' not in session:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    user_logged_in = True

    if user.is_admin:
        # Fetch all rented bikes if user is an admin
        rented_bikes = db_facade.fetch_all_rented_bikes()
    else:
        # Fetch bikes rented by the current user
        rented_bikes = db_facade.fetch_user_rented_bikes(user_id)

    return render_template('rented_bikes.html', rented_bikes=rented_bikes, user_logged_in=user_logged_in,
                           is_admin=user.is_admin, title="My Rented Bikes")


@app.route('/delete-rental/<int:rental_id>', methods=['POST'])
def delete_rental(rental_id):
    if request.method == 'POST':
        # Check if the user is logged in or has admin privileges (if applicable)
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Fetch the rental by its ID
        rental = db_facade.fetch_rental_by_id(rental_id)

        # Check if the rental exists
        if not rental:
            flash("Rental not found", "error")
            return redirect(url_for('rented_bikes'))

        # Delete the rental from the database
        db_facade.delete_rental(rental_id)

        flash("Rental deleted successfully", "success")
        return redirect(url_for('rented_bikes'))
    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/bikes')
def bike_list():
    user_logged_in = 'user_id' in session
    user_is_admin = False
    if user_logged_in:
        # Fetch user details from session or database, assuming User model has an attribute is_admin
        user_id = session['user_id']
        user = db_facade.fetch_user_by_id(user_id)
        user_is_admin = user.is_admin if user else False

    # Fetch all bikes using DatabaseFacade
    bikes = db_facade.fetch_all_available_bikes()

    return render_template('bike_list.html', bikes=bikes, user_logged_in=user_logged_in, user_is_admin=user_is_admin, title="Our Bikes - Bike Rental")


@app.route('/delete-bike/<int:bike_id>', methods=['POST'])
def delete_bike(bike_id):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']
        user = db.session.query(User).get(user_id)

        if not user.is_admin:
            flash("You do not have permission to perform this action", "error")
            return redirect(url_for('bike_list'))

        # Delete the bike from the database
        db_facade.delete_bike_by_id(bike_id)

        flash("Bike deleted successfully", "success")
        return redirect(url_for('bike_list'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/add_bike')
def add_bike():
    user_logged_in = 'user_id' in session
    return render_template('add_bike.html', user_logged_in=user_logged_in, title="Add a bike")


@app.route('/bike-details/<int:bike_id>')
def bike_details(bike_id):
    user_logged_in = 'user_id' in session
    bike = db_facade.fetch_bike_by_id(bike_id)
    if bike:
        return render_template('bike_details.html', bike=bike, user_logged_in=user_logged_in)
    else:
        return render_template('404.html'), 404


@app.route('/photos/<path:filename>')
def serve_image(filename):
    return send_from_directory('photos', filename)


@app.route('/submit-new-bike', methods=['POST'])
def submit_new_bike():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        model = request.form.get('model')
        year = request.form.get('year')
        color = request.form.get('color')
        price = request.form.get('price')

        # Handle the file upload
        if 'image_url' in request.files:
            photo = request.files['image_url']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join('photos', filename)
                photo.save(photo_path)
                image_url = f"photos/{filename}"
            else:
                image_url = None
        else:
            image_url = None

        # Create the bike using the factory pattern
        new_bike = bike_factory.create(name, model, year, color, price, image_url)

        # Add the new bike to the database
        db.session.add(new_bike)
        db.session.commit()

        subject.notify_observers({"bike_model": model})

        # Redirect to the main page or any other appropriate page
        return redirect('/')

    return "Method not allowed", 405


@app.route("/rent/<int:bike_id>", methods=['GET', 'POST'])
def rent_bike(bike_id):
    if 'user_id' not in session:
        flash("You need to log in to rent a bike", "error")
        return redirect(url_for('login'))

    # Get the user ID from the session
    user_id = session['user_id']

    user = db.session.get(User, user_id)
    user_fullname = user.full_name

    # Get the bike object from the database
    bike = db.session.get(Bikes, bike_id)

    # Check if the bike exists
    if not bike:
        flash("Bike not found", "error")
        return redirect(url_for('main'))

    # Inside the rent_bike route
    if request.method == 'POST':
        # Extract form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_decorators = request.form.getlist('decorators')  # Assuming decorators are selected as checkboxes

        # Retrieve bike model and name from the database
        bike_model = bike.model
        bike_name = bike.name
        price_per_day = bike.price

        rental_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days

        # Determine pricing strategy based on the number of days rented
        if rental_days > 30:
            pricing_strategy = MonthlyPricingStrategy()
        else:
            pricing_strategy = StandardPricingStrategy()

        # Calculate total price using selected pricing strategy
        total_price = pricing_strategy.calculate_rental(rental_days, price_per_day)

        # Apply decorator costs
        for decorator_name in selected_decorators:
            if decorator_name == 'ChildSeat':
                bike = ChildSeat(bike)
            elif decorator_name == 'GPS':
                bike = GPS(bike)
            elif decorator_name == 'RoofBag':
                bike = RoofBag(bike)

        # Create Rentals object
        rental = Rentals(
            user_id=user_id,
            user_fullname=user_fullname,
            bike_id=bike_id,
            bike_model=bike_model,
            bike_name=bike_name,
            decorations=', '.join(selected_decorators),  # Join selected decorators into a string
            start_date=start_date,
            end_date=end_date,
            price_per_day=price_per_day,
            total_price=total_price,  # Update total price with decorators
            rental_days=rental_days
        )

        # Save the rental object to the database
        db.session.add(rental)
        db.session.commit()

        # Update the state of the bike to 'rented'
        bike.state = 'rented'
        db.session.commit()

        subject.notify_observers({"bike_model": bike_model, "user_id": user_id})

        # Redirect to the main page or any other appropriate page
        flash("Rental successful", "success")
        return redirect(url_for('main'))

    # Render the rental form template
    return render_template('rent_bike.html', bike=bike, title="")


if __name__ == '__main__':
    app.run(debug=True)
