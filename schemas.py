from flask_marshmallow import Marshmallow
from models import db, User, Menu, Order, Payment, Inventory, Feedback

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class MenuSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Menu

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

class FeedbackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feedback
