import base64
import os
import secrets

LOCAL_DATABASE_USERNAME = 'localuser'
LOCAL_DATABASE_PASSWORD = 'localpassword'
LOCAL_DATABASE_HOST = 'localhost'
LOCAL_DATABASE_NAME = 'carctrl'

LOCAL_KEYCLOAK_URL = "http://localhost:8443"
LOCAL_KEYCLOAK_REALM = "car-control"
LOCAL_KEYCLOAK_CLIENT_ID = "car-control-be"
LOCAL_KEYCLOAK_CLIENT_SECRET = 'B5QemoHBZuDBNmhWv2OuzV1BiFeVQ5QC'

LOCAL_KEYCLOAK_CERTS_URL = f"{LOCAL_KEYCLOAK_URL}/realms/{LOCAL_KEYCLOAK_REALM}/protocol/openid-connect/certs"
LOCAL_KEYCLOAK_INTROSPECTION_URL = f"{LOCAL_KEYCLOAK_URL}/realms/{LOCAL_KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"


class BaseEnvironment:
    """Environment configuration placeholder"""
    FLASK_ENV = os.environ.get('FLASK_ENV', None)
    SECRET_KEY = os.environ.get('SECRET_KEY', base64.b64encode(secrets.token_bytes(32)).decode('utf-8'))
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', None)
    DEBUG = os.environ.get('DEBUG', False)
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 0)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', None)
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', None)
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', None)
    DATABASE_HOST = os.getenv('DATABASE_HOST', None)
    DATABASE_PORT = os.getenv('DATABASE_PORT', None)
    DATABASE_NAME = os.getenv('DATABASE_NAME', None)
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', None)
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', None)
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', None)
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', None)
    KEYCLOAK_INTROSPECTION_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"


class LocalEnvironment(BaseEnvironment):
    FLASK_ENV = os.getenv('FLASK_ENV', 'local')
    SECRET_KEY = os.getenv('SECRET_KEY', 'local_secret_key')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    DEBUG = os.getenv('DEBUG', True)
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 1)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mysql+mysqlconnector')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', LOCAL_DATABASE_USERNAME)
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', LOCAL_DATABASE_PASSWORD)
    DATABASE_HOST = os.getenv('DATABASE_HOST', LOCAL_DATABASE_HOST)
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
    DATABASE_NAME = os.getenv('DATABASE_NAME', LOCAL_DATABASE_NAME)
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', LOCAL_KEYCLOAK_URL)
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', LOCAL_KEYCLOAK_REALM)
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', LOCAL_KEYCLOAK_CLIENT_ID)
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', LOCAL_KEYCLOAK_CLIENT_SECRET)
    KEYCLOAK_INTROSPECTION_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"


class LocalMariaDBEnvironment(BaseEnvironment):
    FLASK_ENV = os.getenv('FLASK_ENV', 'local-mariadb')
    SECRET_KEY = os.getenv('SECRET_KEY', 'local_secret_key')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    DEBUG = os.getenv('DEBUG', True)
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 1)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mariadb+mariadbconnector')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'localuser')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'localpassword')
    # TODO: check why socket connector is used:
    #  https://stackoverflow.com/questions/4448467/cant-connect-to-local-mysql-server-through-socket-var-lib-mysql-mysql-sock
    # DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_HOST = os.getenv('DATABASE_HOST', '127.0.0.1')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3307')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'carctrl')
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', LOCAL_KEYCLOAK_URL)
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', LOCAL_KEYCLOAK_REALM)
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', LOCAL_KEYCLOAK_CLIENT_ID)
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', LOCAL_KEYCLOAK_CLIENT_SECRET)
    KEYCLOAK_INTROSPECTION_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"


# Just an example placeholder. With current setup it will not work.
class DevelopmentEnvironment(BaseEnvironment):
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'development_secret_key')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    DEBUG = os.getenv('DEBUG', False)
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 0)
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mysql+mysqlconnector')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'developmentuser')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'developmentpassword')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'carctrl')
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', LOCAL_KEYCLOAK_URL)
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', LOCAL_KEYCLOAK_REALM)
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', LOCAL_KEYCLOAK_CLIENT_ID)
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', LOCAL_KEYCLOAK_CLIENT_SECRET)
    KEYCLOAK_INTROSPECTION_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
