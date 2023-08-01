import time
from typing import Dict, Optional

from google.auth import jwt
from google.auth.crypt import RSASigner

TOKEN_VALID_DURATION_IN_SECONDS = 3600
TOKEN_RENEW_DURATION_IN_SECONDS = 300  # Renew token if less than 5 minutes remain

class TokenManager:
    """
    Manages generation and refreshing of JWT tokens.
    Tokens are automatically refreshed if they are close to expiry.
    """
    def __init__(self, service_account_email: str, service_account_auth_file: str) -> None:
        self._service_account_email = service_account_email
        self._service_account_auth_file = service_account_auth_file
        self._token: Optional[str] = None
        self._expiration: int = 0

    def _generate_token(self) -> None:
        """Generate a new JWT token and update the expiration time."""
        signer: RSASigner = self._get_signer_from_service_account_file()
        expiration_time: int = self._get_expiration_time()
        payload: Dict = self._create_payload(expiration_time)

        jwt_token: str = jwt.encode(signer=signer, payload=payload).decode("ascii")
        self._token = jwt_token
        self._expiration = expiration_time

    def _get_signer_from_service_account_file(self) -> RSASigner:
        """Return an RSA signer using the service account file."""
        return RSASigner.from_service_account_file(self._service_account_auth_file)

    def _get_expiration_time(self) -> int:
        """Return the expiration time for the token."""
        return int(time.time()) + TOKEN_VALID_DURATION_IN_SECONDS

    def _create_payload(self, expiration_time: int) -> Dict:
        """Return the payload for the JWT token."""
        return {"email": self._service_account_email, "exp": expiration_time}

    def _is_token_close_to_expiring(self) -> bool:
        return time.time() > self._expiration - TOKEN_RENEW_DURATION_IN_SECONDS

    @property
    def token(self) -> str:
        """Return a valid JWT token, generating a new one if necessary."""
        if self._token is None or self._is_token_close_to_expiring():
            self._generate_token()
        return self._token
