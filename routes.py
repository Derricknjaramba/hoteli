from flask import Flask, request, jsonify, abort
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Menu, Order, Payment, Inventory, Feedback
from schemas import UserSchema, MenuSchema, OrderSchema, PaymentSchema, InventorySchema, FeedbackSchema
from werkzeug.exceptions import BadRequest
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize JWTManager
jwt = JWTManager(app)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize DB
db.init_app(app)

# Error handling
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'message': str(error)}), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({'message': 'Internal server error'}), 500

# User Registration
@app.route('/register', methods=['POST'])
def register_user():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        raise BadRequest('Username and Password are required')

    username = request.json['username']
    password = request.json['password']
    role = request.json.get('role', 'guest')

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(UserSchema().dump(new_user)), 201

# User Login (JWT Token)
@app.route('/login', methods=['POST'])
def login_user():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        raise BadRequest('Username and Password are required')

    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Manager Routes

# Create Menu Item (Manager only)
@app.route('/menu', methods=['POST'])
@jwt_required()
def add_menu():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    
    if user.role != 'manager':
        return jsonify({'message': 'Access forbidden: manager role required'}), 403

    if not request.json or 'name' not in request.json:
        raise BadRequest('Menu name is required')

    new_item = Menu(
        name=request.json['name'],
        category=request.json['category'],
        price=request.json['price'],
        description=request.json.get('description', '')
    )
    db.session.add(new_item)
    db.session.commit()

    return jsonify(MenuSchema().dump(new_item)), 201

# Place Order (Guest only)
@app.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    
    if user.role != 'guest':
        return jsonify({'message': 'Access forbidden: guest role required'}), 403

    if not request.json or 'menu_item_id' not in request.json:
        raise BadRequest('Menu item ID is required')

    new_order = Order(
        guest_id=current_user,
        menu_item_id=request.json['menu_item_id']
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify(OrderSchema().dump(new_order)), 201

# Submit Feedback (Guest only)
@app.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    
    if user.role != 'guest':
        return jsonify({'message': 'Access forbidden: guest role required'}), 403

    if not request.json or 'rating' not in request.json:
        raise BadRequest('Rating is required')

    new_feedback = Feedback(
        guest_id=current_user,
        rating=request.json['rating'],
        comments=request.json.get('comments', '')
    )
    db.session.add(new_feedback)
    db.session.commit()

    return jsonify(FeedbackSchema().dump(new_feedback)), 201

# General Routes for Managers (menu, orders, etc.) are secured with `@jwt_required()`

# Initialize DB and Run the App
if __name__ == '__main__':
    app.run(debug=True)
