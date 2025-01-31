from cg_lims.clients.smrt_link.smrt_link_client import SmrtLinkClient

DEFAULT_HTTPS = False
PORT = 8243


class SmrtLinkConfig:
    """Class for handling the SMRT Link API configurations."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = PORT,
        verify: bool = DEFAULT_HTTPS,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.verify = verify

    def client(self):
        """Initialize the SMRT Link API client."""
        return SmrtLinkClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            verify=self.verify,
        )
