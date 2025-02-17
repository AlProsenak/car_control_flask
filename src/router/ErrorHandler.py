from flask import Blueprint

from src.util.RouterUtil import create_error_response

error_handler_bp = Blueprint('error_handler', __name__)

# For router local error handler use `errorhandler()` inside the router instead.
@error_handler_bp.app_errorhandler(400)
def bad_request(error):
    return create_error_response(400, error.description)


@error_handler_bp.app_errorhandler(404)
def not_found(error):
    return create_error_response(404, error.description)


@error_handler_bp.app_errorhandler(500)
def internal_server_error(error):
    return create_error_response(500, error.description)
