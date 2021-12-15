import pytest
from genologics.entities import Process

from cg_lims.EPPs.udf.set.set_method import get_document_paths
from datetime import datetime as dt

from tests.conftest import (
    server,
)
import responses
import requests


@responses.activate
def mock_responces():
    document_title = "Some Atlas Method Title"
    atlas_document_path = "atlas/document/path.md"
    atlas_host = "atlas/api"
    document_udf = "Method Document"
    responses.add(
        responses.GET,
        f"{atlas_host}/{document_title}/path",
        json=atlas_document_path,
        status=200,
        ok=True,
    )
    return responses


@pytest.fixture
def mock_session(mocker):
    mock_session = mocker.patch.object(requests.get)
    mock_session


def test_set_method(mocker, lims):
    # GIVEN: ".

    server("flat_tests")

    document_title = "Some Atlas Method Title"
    atlas_document_path = "atlas/document/path.md"
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = document_title
    process.put()

    # WHEN running get_document_paths
    with mocker.patch("requests.get") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.side_effect = mock_responces()
        document_paths = get_document_paths(
            process=process, document_udfs=[document_udf], atlas_host="atlas/api"
        )

    # THEN assert the delivery date was set to todays date
    assert document_paths == [atlas_document_path]
