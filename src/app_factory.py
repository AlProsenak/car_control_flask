from flask import Flask
from flask_cors import CORS

from .extensions import db, ma, migrate

from src.config.EnvironmentConfig import LocalConfig, DevelopmentConfig, LocalMariaDBConfig


def initialize(environment='local'):
    app = Flask(__name__)

    # Initialize environment configuration
    if environment == 'local':
        config_object = LocalConfig()
    elif environment == 'local-mariadb':
        config_object = LocalMariaDBConfig()
    elif environment == 'development':
        config_object = DevelopmentConfig()
    else:
        raise ValueError('Invalid environment value: ' + environment)

    app.config.from_object(config_object)

    origins_str = config_object.CORS_ORIGINS
    if origins_str:
        # Parse and remove blank strings
        allowed_origins = [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    else:
        allowed_origins = []

    CORS(app, origins=allowed_origins)

    print(f"Initializing application with environment: {environment}")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    # Initialize Flask-Migrate extension, which allows for `flask db` migration commands to be run
    migrate.init_app(app, db, directory='src/db/migration')

    return app
