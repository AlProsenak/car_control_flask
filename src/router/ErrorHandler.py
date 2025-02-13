from datetime import datetime
from flask import Blueprint, jsonify

error_handler_bp = Blueprint('error_handler', __name__)

# `app_errorhandler()` is global. For local custom error handler use `errorhandler()` inside the route.
@error_handler_bp.app_errorhandler(400)
def bad_request(error):
    response = jsonify({
        "status": 400,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }), 400
    return response


@error_handler_bp.app_errorhandler(404)
def not_found(error):
    response = jsonify({
        "status": 404,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }), 404
    return response


@error_handler_bp.app_errorhandler(500)
def internal_server_error(error):
    response = jsonify({
        "status": 500,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }), 500
    return response
