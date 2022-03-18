import pytest
from genologics.entities import Process

from cg_lims.EPPs.udf.set.set_method import get_path
from cg_lims.exceptions import AtlasResponseFailedError
from tests.conftest import (
    server,
)

import responses
import requests
import logging


@pytest.fixture()
@responses.activate
def atlas_response_mock():
    atlas_document_path = "atlas/document/path.md"
    url = "https://atlas/api/SomeTitle/path"
    responses.add(responses.GET, url, json=atlas_document_path, status=200)
    return requests.get(url)


def test_get_path(lims, mocker, atlas_response_mock):
    # GIVEN: a lims with a process: id="24-196211"
    # with a udf named "Method Document" with a value of some method document title in atlas: "SomeTitle"  and
    # GIVEN: a atlas api with a endpoint "https://atlas/api/SomeTitle/path" returning "atlas/document/path.md"

    server("flat_tests")
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = "SomeTitle"
    process.put()
    mocker.patch.object(requests, "get")
    requests.get.return_value = atlas_response_mock

    # WHEN running get_path with the process, the atlas api host and the document udf
    document_path = get_path(
        process=process, document_title="SomeTitle", atlas_host="https://atlas/api"
    )

    # THEN assert get_path returns the document path
    assert document_path == "atlas/document/path.md"


@pytest.fixture()
@responses.activate
def atlas_response_mock_fail():
    url = "https://atlas/api/SomeTitle/path"
    responses.add(responses.GET, url, status=404, json={"detail": "document not found"})
    return requests.get(url)


def test_get_path_wrong_document_title(lims, mocker, atlas_response_mock_fail):
    # GIVEN: a lims with a process: id="24-196211"
    # with a udf named "Method Document" with a value of some method document title that dont exist in atlas: "SomeWrongTitle"  and
    # GIVEN: a atlas api with a endpoint "https://atlas/api/SomeTitle/path" returning "atlas/document/path.md"

    server("flat_tests")
    document_udf = "Method Document"
    process = Process(lims=lims, id="24-196211")
    process.udf[document_udf] = "SomeWrongTitle"
    process.put()
    mocker.patch.object(requests, "get")
    requests.get.return_value = atlas_response_mock_fail

    # WHEN running get_path with the process, the atlas api host and the document udf.
    # THEN: assert AtlasResponseFailedError is being raised
    with pytest.raises(AtlasResponseFailedError) as error:
        document_path = get_path(
            process=process, document_title="SomeWrongTitle", atlas_host="https://atlas/api"
        )

    # THEN: assert the error message is fetched from the api response
    assert error.value.message == '404 : {"detail": "document not found"}'
