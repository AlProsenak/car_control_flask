from typing import Optional

import requests

from src.extensions import config

# TODO: make an enum
RS256_ALGORITHM = 'RS256'


def get_iam_certificate() -> Optional[dict]:
    return get_keycloak_certificate()


def get_keycloak_certificate() -> Optional[dict]:
    try:
        keycloak_certs_url = config.get_instance().KEYCLOAK_CERTS_URL
        response = requests.get(keycloak_certs_url)
        response.raise_for_status()

        certificate_data = response.json()
        certification_keys: list[object] = certificate_data.get("keys", [])
        certification_key = extract_certification_key(certification_keys, RS256_ALGORITHM)

        if certification_key is None:
            return None
        return certification_key
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        print(f"Error fetching public key: {e}")
        return None


def extract_certification_key(certification_keys: Optional[list[object]], desired_key_algorithm: str) -> Optional[dict]:
    if not certification_keys:
        return None

    first_found_valid_key = None
    for key in certification_keys:
        algorithm = key.get("alg", None)
        certificate_chain = key.get("x5c", None)

        if is_key_valid(algorithm, certificate_chain):
            if algorithm == desired_key_algorithm:
                # TODO: Function argument that allows for different key formats
                certificate = set_to_pem_rsa_public_format(certificate_chain[0])
                return build_certificate_key(algorithm, certificate)
            elif not first_found_valid_key:
                certificate = set_to_pem_rsa_public_format(certificate_chain[0])
                first_found_valid_key = build_certificate_key(algorithm, certificate)

    # Return first viable key if key with desirable algorithm was not found
    if not first_found_valid_key:
        return None
    return first_found_valid_key


def is_key_valid(algorithm: str, certificate: list[str]):
    return algorithm and certificate and certificate[0]


def set_to_pem_rsa_public_format(key: str) -> Optional[str]:
    if key is None:
        return None
    return "-----BEGIN PUBLIC KEY-----\n" + key + "\n-----END PUBLIC KEY-----"


def build_certificate_key(algorithm: str, certificate: str):
    return {
        "algorithm": algorithm,
        "certificate": certificate,
    }


def verify_jwt(token) -> bool:
    return introspect_keycloak_jwt_token(token)


def introspect_keycloak_jwt_token(token) -> bool:
    if token is None:
        return False

    conf = config.get_instance()
    keycloak_client_id = conf.KEYCLOAK_CLIENT_ID
    keycloak_client_secret = conf.KEYCLOAK_CLIENT_SECRET
    keycloak_introspection_url = conf.KEYCLOAK_INTROSPECTION_URL

    payload = {
        'token': token,
        'client_id': keycloak_client_id,
        'client_secret': keycloak_client_secret,
    }
    try:
        # Token metadata API
        response = requests.post(keycloak_introspection_url, data=payload)
        response.raise_for_status()
        data = response.json()

        # Validate if token is active
        return data.get('active', False)
    except requests.exceptions.RequestException as e:
        print(f"Error introspecting token: {e}")
        return False
