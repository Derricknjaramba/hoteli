from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from werkzeug.exceptions import BadRequest
from config import Config

# Initialize the DB object (no need to initialize here, will do it in create_app)
db = SQLAlchemy()

# Initialize JWTManager and Marshmallow
jwt = JWTManager()
ma = None

# Initialize Flask-Migrate
migrate = None

# Setup logging (will be initialized in the create_app method)
logger = None

def setup_logging(app):
    """Setup logging before the first request."""
    logging.basicConfig(level=Config.LOGGING_LEVEL)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Starting Hotel Management System API")


def create_app():
    # Initialize the Flask app object first
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize JWTManager, Marshmallow, and Migrate after app is created
    jwt.init_app(app)
    
    global ma
    from flask_marshmallow import Marshmallow
    ma = Marshmallow(app)
    
    # Initialize the DB object here with app
    db.init_app(app)
    
    # Initialize Migrate here with app and db
    global migrate
    migrate = Migrate(app, db)

    # Import your models after db is initialized
    from models import User, Menu, Order, Payment, Inventory, Feedback

    # Call setup_logging after app is fully initialized
    setup_logging(app)

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

        return jsonify(ma.dump(new_user)), 201

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

        return jsonify(ma.dump(new_item)), 201

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

        return jsonify(ma.dump(new_order)), 201

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

        return jsonify(ma.dump(new_feedback)), 201

    return app


# If this script is being run directly (not via the Flask CLI), start the app.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
