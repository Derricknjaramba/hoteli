import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hotel_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # For Flask sessions
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')  # JWT Secret Key
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour expiry for JWT tokens
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')  # Default log level
