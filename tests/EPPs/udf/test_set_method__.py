from genologics.entities import Process

from cg_lims.EPPs.udf.set.set_method import get_document_paths
from datetime import datetime as dt

from unittest.mock import patch

from tests.conftest import (
    server,
)
import responses
import requests


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, ok):
            self.json_data = json_data
            self.status_code = status_code
            self.ok = True

        def json(self):
            return self.json_data

    print("args:" + args[0])
    if args[0] == "atlas/api/title/Some Atlas Method Title/path":
        return MockResponse("atlas/document/path.md", 200, True)
    return MockResponse(None, 404, False)


"""def test_set_delivered(lims):
    # GIVEN: ".

    server("flat_tests")

    document_title = "Some Atlas Method Title"
    atlas_document_path = "atlas/document/path.md"
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = document_title
    process.put()

    # WHEN running get_document_paths
    with patch("requests.get") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.side_effect = mocked_requests_get
        document_paths = get_document_paths(
            process=process, document_udfs=[document_udf], atlas_host="atlas/api"
        )

    # THEN assert the delivery date was set to todays date
    assert document_paths == [atlas_document_path]
"""


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


def test_set_delivered(lims):
    # GIVEN: ".

    server("flat_tests")

    document_title = "Some Atlas Method Title"
    atlas_document_path = "atlas/document/path.md"
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = document_title
    process.put()

    # WHEN running get_document_paths
    with patch("requests.get") as mock_request:
        mock_request.side_effect = mock_responces
        document_paths = get_document_paths(
            process=process, document_udfs=[document_udf], atlas_host="atlas/api"
        )

    # THEN assert the delivery date was set to todays date
    assert document_paths == [atlas_document_path]


"""@responses.activate
def test_set_delivered_(lims):
    # GIVEN: ".

    server("flat_tests")

    document_title = "Some Atlas Method Title"
    atlas_document_path = "atlas/document/path.md"
    atlas_host = "atlas/api"
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = document_title
    process.put()
    responses.add(
        responses.GET,
        f"{atlas_host}/{document_title}/path",
        json=atlas_document_path,
        status=200,
        ok=True,
    )

    # WHEN running get_document_paths
    document_paths = get_document_paths(
        process=process, document_udfs=[document_udf], atlas_host=atlas_host
    )

    # THEN assert the delivery date was set to todays date
    assert document_paths == [atlas_document_path]
"""
