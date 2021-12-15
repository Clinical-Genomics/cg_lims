import pytest
from genologics.entities import Process

from cg_lims.EPPs.udf.set.set_method import get_document_paths
from datetime import datetime as dt

from tests.conftest import (
    server,
)

import responses
import requests
from requests import Request


@pytest.fixture()
@responses.activate
def mock_responces():
    document_title = "SomeTitle"
    atlas_document_path = "atlas/document/path.md"
    atlas_host = "https://atlas/api"
    url = f"{atlas_host}/{document_title}/path"
    responses.add(responses.GET, url, json=atlas_document_path, status=200)
    return requests.get(url)


def test_set_method(lims, mocker, mock_responces):
    # GIVEN: ".

    server("flat_tests")

    document_title = "SomeTitle"
    atlas_document_path = "atlas/document/path.md"
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = document_title
    process.put()

    # WHEN running get_document_paths
    mocker.patch.object(requests, "get")
    requests.get.return_value = mock_responces

    document_paths = get_document_paths(
        process=process, document_udfs=[document_udf], atlas_host="https://atlas/api"
    )

    # THEN assert the delivery date was set to todays date
    assert document_paths == [atlas_document_path]
