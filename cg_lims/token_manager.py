import time
from google.auth import jwt
from google.auth.crypt import RSASigner

TOKEN_VALID_DURATION_IN_SECONDS = 3600

class TokenManager:
    """Manages generation and refreshing of JWT tokens."""

    def __init__(self, service_account_email: str, service_account_auth_file: str):
        self._service_account_email = service_account_email
        self._service_account_auth_file = service_account_auth_file
        self._token = None
        self._expiration = None

    def _generate_token(self) -> None:
        """Generate a new JWT token and update the expiration time."""
        signer = self._get_signer_from_service_account_file()
        expiration_time = self._get_expiration_time()
        payload = self._create_payload(expiration_time)

        jwt_token = jwt.encode(signer=signer, payload=payload).decode("ascii")
        self._token = jwt_token
        self._expiration = expiration_time

    def _get_signer_from_service_account_file(self):
        """Return an RSA signer using the service account file."""
        return RSASigner.from_service_account_file(self._service_account_auth_file)

    def _get_expiration_time(self):
        """Return the expiration time for the token."""
        return int(time.time()) + TOKEN_VALID_DURATION_IN_SECONDS

    def _create_payload(self, expiration_time):
        """Return the payload for the JWT token."""
        return {"email": self._service_account_email, "exp": expiration_time}

    @property
    def token(self):
        """Return a valid JWT token, generating a new one if necessary."""
        if not self._token or time.time() > self._expiration:
            self._generate_token()
        return self._token
