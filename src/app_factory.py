from flask import Flask

from .extensions import db, ma, migrate

from src.config.EnvironmentConfig import LocalConfig, DevelopmentConfig


def initialize(environment='local'):
    app = Flask(__name__)

    # Initialize environment configuration
    if environment == 'local':
        app.config.from_object(LocalConfig)
    elif environment == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        raise ValueError('Invalid environment value: ' + environment)

    print(f"Initializing application with environment: {environment}")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    # Initialize Flask-Migrate extension, which allows for `flask db` migration commands to be run
    migrate.init_app(app, db, directory='src/db/migration')

    return app
