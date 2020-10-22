import pytest
from genologics.lims import Lims



@pytest.fixture
def config():
    """Get file path to invalid csv"""

    return "tests/fixtures/config.yaml"


@pytest.fixture
def lims():
    url = 'http://testgenologics.com:4040'
    username = 'test'
    password = 'password'  
    return Lims(url, username=username, password=password)