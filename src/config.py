class Config:
    """Environment configuration placeholder"""
    FLASK_ENV = 'placeholder'
    SECRET_KEY = 'secret_key_placeholder'
    DATABASE_DRIVER = 'database_driver_placeholder'
    DATABASE_USERNAME = 'database_username_placeholder'
    DATABASE_PASSWORD = 'database_password_placeholder'
    DATABASE_HOST = 'database_host_placeholder'
    DATABASE_PORT = 'database_port_placeholder'
    DATABASE_NAME = 'database_name_placeholder'
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


class LocalConfig(Config):
    FLASK_ENV = 'local'
    SECRET_KEY = 'local_secret_key'
    DEBUG = True
    FLASK_DEBUG = 1
    DATABASE_DRIVER = 'mysql+mysqlconnector'
    DATABASE_USERNAME = 'localuser'
    DATABASE_PASSWORD = 'localpassword'
    DATABASE_HOST = 'localhost'
    DATABASE_PORT = '3306'
    DATABASE_NAME = 'carctrl'
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    SECRET_KEY = 'development_secret_key'
    DEBUG = False
    FLASK_DEBUG = 0
    DATABASE_DRIVER = 'mysql+mysqlconnector'
    DATABASE_USERNAME = 'developmentuser'
    DATABASE_PASSWORD = 'developmentpassword'
    DATABASE_HOST = 'localhost'
    DATABASE_PORT = '3306'
    DATABASE_NAME = 'carctrl'
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
