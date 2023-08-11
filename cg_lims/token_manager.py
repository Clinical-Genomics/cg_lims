import logging
from google.oauth2 import service_account
import google.auth.transport.requests

LOG = logging.getLogger(__name__)


class TokenManager:
    """Manages generation and refreshing of JWT tokens."""

    def __init__(
        self, service_account_email: str, service_account_auth_file: str, audience: str
    ) -> None:
        self._service_account_email = service_account_email
        self._service_account_auth_file = service_account_auth_file
        self.audience = audience


    def get_token(self) -> str:
        """Get a valid JWT token."""
        credentials = service_account.IDTokenCredentials.from_service_account_file(
            self._service_account_auth_file,
            target_audience=self.audience,
        )

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token
