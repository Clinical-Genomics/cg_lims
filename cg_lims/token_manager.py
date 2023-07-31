import time
from google.auth import jwt
from google.auth.crypt import RSASigner


class TokenManager:
    def __init__(self, service_account_email: str, service_account_auth_file: str):
        self._service_account_email: str = service_account_email
        self._service_account_auth_file: str = service_account_auth_file
        self._token = None
        self._expiration = None

    def _generate_token(self) -> None:
        signer = RSASigner.from_service_account_file(self._service_account_auth_file)
        expiration_time = int(time.time()) + 3600
        payload = {"email": self._service_account_email, "exp": expiration_time}
        jwt_token = jwt.encode(signer=signer, payload=payload).decode("ascii")
        self._token = jwt_token
        self._expiration = expiration_time

    @property
    def token(self):
        if not self._token or time.time() > self._expiration:
            self._generate_token()
        return self._token
