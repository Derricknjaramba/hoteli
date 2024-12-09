from flask_sqlalchemy import SQLAlchemy

# Create an instance of SQLAlchemy
db = SQLAlchemy()

# User Model (Manager and Guest)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'manager' or 'guest'

    # Hash password before storing it in the DB
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check password validity
    def check_password(self, password):
        return check_password_hash(self.password, password)


# Menu Model
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Menu {self.name}>"


# Order Model (Relation between Guest and Menu Item)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)

    guest = db.relationship('User', backref=db.backref('orders', lazy=True))
    menu_item = db.relationship('Menu', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.id}, Guest: {self.guest_id}, Item: {self.menu_item_id}>"


# Payment Model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., 'credit_card', 'cash', 'paypal'

    order = db.relationship('Order', backref=db.backref('payment', uselist=False))

    def __repr__(self):
        return f"<Payment {self.id}, Order ID: {self.order_id}, Amount: {self.amount}>"


# Inventory Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    menu_item = db.relationship('Menu', backref=db.backref('inventory', lazy=True))

    def __repr__(self):
        return f"<Inventory Item {self.menu_item.name}, Quantity: {self.quantity}>"


# Feedback Model (For Guests to provide feedback)
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating between 1-5
    comments = db.Column(db.String(255), nullable=True)

    guest = db.relationship('User', backref=db.backref('feedbacks', lazy=True))

    def __repr__(self):
        return f"<Feedback {self.id}, Guest: {self.guest_id}, Rating: {self.rating}>"

