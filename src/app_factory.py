from flask import Flask
from flask_cors import CORS

from .auth.Security import get_iam_certificate
from .extensions import db, ma, migrate, jwt, config


def initialize(environment='local'):
    app = Flask(__name__)

    config.init_config(environment)
    config_object = config.get_instance()

    app.config.from_object(config_object)

    # Configure security
    public_certificate = get_iam_certificate()
    if not public_certificate:
        print("Failed to load IAM public key. JWT authentication will not work.")
        exit(1)

    app.config['JWT_ALGORITHM'] = public_certificate['algorithm']
    app.config['JWT_PUBLIC_KEY'] = public_certificate['certificate']
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']

    # Configure CORS
    origins_str = config_object.CORS_ORIGINS
    if origins_str:
        # Parse and remove blank strings
        allowed_origins = [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    else:
        allowed_origins = []

    CORS(app, origins=allowed_origins)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db, directory='src/db/migration')
    jwt.init_app(app)

    print(f"Initialized application with environment: {environment}")

    return app
