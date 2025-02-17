from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request

from src.auth.Security import verify_jwt
from src.util.RouterUtil import create_error_response


def jwt_required_custom():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # TODO: figure out why Flask-JWT-Extended is not being able to parse public key. Error:
                #  InvalidKeyError('Could not parse the provided public key.')
                # verify_jwt_in_request()

                authorization_token = request.headers.get("Authorization", None)

                if not authorization_token:
                    return create_error_response(401, "Missing token")

                bearer_token = authorization_token.split("Bearer ")[1]

                if not verify_jwt(bearer_token):
                    return create_error_response(401, "Invalid or expired token")
            except Exception as e:
                print(f"Caught JWT verification error: {e}")
                return create_error_response(401, "Missing or invalid token")

            return fn(*args, **kwargs)

        return decorator

    return wrapper
