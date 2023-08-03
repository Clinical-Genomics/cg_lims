import time

import pytest
from pytest_mock import MockFixture

from cg_lims.exceptions import ServiceAccountFileError
from cg_lims.token_manager import TOKEN_RENEW_DURATION_IN_SECONDS, TokenManager


class TestTokenManager:
    @pytest.fixture(autouse=True)
    def mock_dependencies(self, mocker: MockFixture):
        self.mock_encode = mocker.patch(
            "cg_lims.token_manager.jwt.encode", return_value=b"test_token"
        )
        self.mock_from_service_account_file = mocker.patch(
            "cg_lims.token_manager.RSASigner.from_service_account_file",
            return_value=mocker.MagicMock(),
        )
        yield

    def test_get_token(self, token_manager: TokenManager):
        # WHEN a token is requested
        token = token_manager.get_token()

        # THEN a token should be returned
        assert token == "test_token"

    def test_get_token_existing_token_valid(self, token_manager: TokenManager):
        # GIVEN an existing valid token
        token_manager._token = "valid_token"
        token_manager._expiration = time.time() + 1000

        # WHEN a token is requested
        actual_token = token_manager.get_token()

        # THEN the existing token should be returned
        assert actual_token == "valid_token"

    def test_get_token_existing_token_expired(self, token_manager: TokenManager):
        # GIVEN an expired token
        token_manager._token = "expired_token"
        token_manager._expiration = time.time() - 1000

        # GIVEN the next token that will be generated
        self.mock_encode.return_value = b"next_token"

        # WHEN a token is requested
        actual_token = token_manager.get_token()

        # THEN the next token should be returned
        assert actual_token == "next_token"

    def test_get_token_close_to_expiry(self, token_manager: TokenManager):
        # GIVEN an existing token close to expiry
        token_manager._token = "almost_expired_token"
        token_manager._expiration = time.time() + TOKEN_RENEW_DURATION_IN_SECONDS - 10

        # GIVEN the next token that will be generated
        self.mock_encode.return_value = b"next_token"

        # WHEN a token is requested
        actual_token = token_manager.get_token()

        # THEN the next token should be returned
        assert actual_token == "next_token"


def test_service_account_file_not_found(tmp_path):
    # GIVEN a non-existing service account file
    non_existing_file = tmp_path / "non_existing_file.json"

    # GIVEN a TokenManager with the non-existing service account file
    token_manager = TokenManager("test_email", str(non_existing_file))

    # WHEN a token is retrieved
    # THEN a ServiceAccountFileError should be raised
    with pytest.raises(ServiceAccountFileError):
        token_manager.get_token()
