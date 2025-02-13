import os

from src import app_factory
from src.router.ErrorHandler import error_handler_bp
from src.router.VehicleRouter import vehicle_router_bp

environment: str = os.environ.get('FLASK_ENV', 'local')
app = app_factory.initialize(environment)

app.register_blueprint(vehicle_router_bp)
app.register_blueprint(error_handler_bp)

if __name__ == '__main__':
    app.run()
