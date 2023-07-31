import time
from google.auth import jwt
from google.auth.crypt import RSASigner


class AuthenticationService:
    def __init__(self, service_account: str, service_account_auth_file: str):
        self.service_account = service_account
        self.service_account_auth_file = service_account_auth_file
        self._token = None
        self._expiration = None

    def generate_token(self):
        signer = RSASigner.from_service_account_file(self.service_account_auth_file)
        expiration_time = int(time.time()) + 3600
        payload = {"email": self.service_account, "exp": expiration_time}
        jwt_token = jwt.encode(signer=signer, payload=payload).decode("ascii")
        self._token = jwt_token
        self._expiration = expiration_time

    @property
    def token(self):
        if not self._token or time.time() > self._expiration:
            self.generate_token()
        return self._token
