import os

from flask_migrate import upgrade

from src import app_factory
from src.router.ErrorHandler import error_handler_bp
from src.router.VehicleRouter import vehicle_router_bp
from src.util.TestDataGenerator import initialize_test_data

environment: str = os.environ.get('FLASK_ENV', 'local')
app = app_factory.initialize(environment)

# Auto apply migrations
with app.app_context():
    upgrade()

# Auto generate test data for development environments
if environment in ('local', 'local-mariadb'):
    with app.test_request_context():
        initialize_test_data()

app.register_blueprint(vehicle_router_bp)
app.register_blueprint(error_handler_bp)

if __name__ == '__main__':
    app.run()
