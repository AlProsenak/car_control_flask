import os

from flask_migrate import upgrade

from src import app_factory
from src.router.ErrorHandler import error_handler_bp
from src.router.VehicleRouter import vehicle_router_bp

from flask_cors import CORS

environment: str = os.environ.get('FLASK_ENV', 'local')
app = app_factory.initialize(environment)

# Auto apply migrations
with app.app_context():
    upgrade()

# TODO: if development environment populate database with dummy data

app.register_blueprint(vehicle_router_bp)
app.register_blueprint(error_handler_bp)

CORS(app)

if __name__ == '__main__':
    app.run()
