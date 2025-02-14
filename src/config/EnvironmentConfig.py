import base64
import os
import secrets


class Config:
    """Environment configuration placeholder"""
    FLASK_ENV = os.environ.get('FLASK_ENV', 'placeholder')
    SECRET_KEY = os.environ.get('SECRET_KEY', base64.b64encode(secrets.token_bytes(32)).decode('utf-8'))
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', None)
    DEBUG = os.environ.get('DEBUG', False)
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 0)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', None)
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', None)
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', None)
    DATABASE_HOST = os.getenv('DATABASE_HOST', None)
    DATABASE_PORT = os.getenv('DATABASE_PORT', None)
    DATABASE_NAME = os.getenv('DATABASE_NAME', None)
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


class LocalConfig(Config):
    FLASK_ENV = os.getenv('FLASK_ENV', 'local')
    SECRET_KEY = os.getenv('SECRET_KEY', 'local_secret_key')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    DEBUG = os.getenv('DEBUG', True)
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 1)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mysql+mysqlconnector')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'localuser')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'localpassword')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'carctrl')
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


class DevelopmentConfig(Config):
    FLASK_ENV = os.getenv('FLASK_ENV', 'local')
    SECRET_KEY = os.getenv('SECRET_KEY', 'local_secret_key')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    DEBUG = os.getenv('DEBUG', False)
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 0)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mysql+mysqlconnector')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'developmentuser')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'developmentpassword')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'carctrl')
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
