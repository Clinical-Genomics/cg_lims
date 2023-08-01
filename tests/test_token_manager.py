import pytest
from pytest_mock import MockFixture
import time
from cg_lims.token_manager import TokenManager


class TestTokenManager:
    @pytest.fixture(autouse=True)
    def mock_dependencies(self, mocker: MockFixture):
        self.mock_encode = mocker.patch("cg_lims.token_manager.jwt.encode", return_value=b"test_token")
        self.mock_from_service_account_file = mocker.patch(
            "cg_lims.token_manager.RSASigner.from_service_account_file",
            return_value=mocker.MagicMock(),
        )
        yield

    def test_token_property_new_token_needed(self, token_manager: TokenManager):
        # WHEN the token property is accessed
        actual_token = token_manager.token

        # THEN a new token should be generated
        assert actual_token == "test_token"

    def test_token_property_existing_token_valid(self, token_manager: TokenManager):
        # GIVEN an existing valid token
        token_manager._token = "existing_token"
        token_manager._expiration = time.time() + 1000

        # WHEN the token property is accessed
        actual_token = token_manager.token

        # THEN the existing token should be returned
        assert actual_token == "existing_token"

    def test_token_property_existing_token_expired(self, token_manager: TokenManager):
        # GIVEN an expired token
        token_manager._token = "expired_token"
        token_manager._expiration = time.time() - 1000

        # WHEN the token property is accessed
        self.mock_encode.return_value = b"new_token"
        actual_token = token_manager.token

        # THEN a new token should be generated
        assert actual_token == "new_token"
