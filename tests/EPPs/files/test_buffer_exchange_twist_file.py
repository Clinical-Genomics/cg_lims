from tests.conftest import server
from pathlib import Path

from genologics.entities import Artifact

import pytest

from cg_lims.EPPs.files.hamilton.buffer_exchange_twist_file import get_file_data_and_write
from cg_lims.exceptions import MissingUDFsError


def test_get_file_data_and_write(lims, hamilton_buffer_exchange):
    # GIVEN a file name and a list of artifacts with all required udf:s and assorted wells.
    server("buffer_exchange_twist_file")
    file_name = "file_name_1"
    file = Path(file_name)
    artifacts = [
        Artifact(lims, id="2-2336703"),
        Artifact(lims, id="2-2336704"),
        Artifact(lims, id="2-2336705"),
        Artifact(lims, id="2-2336706"),
        Artifact(lims, id="2-2336707"),
    ]

    # WHEN running get_file_data_and_write
    get_file_data_and_write(artifacts, file)

    # THEN the file has been created and the file content is as expected.
    assert file.read_text() == hamilton_buffer_exchange
    file.unlink()


def test_get_file_data_and_write_missing_udfs(lims, hamilton_buffer_exchange_no_udf):
    # GIVEN a file name and a list of artifacts where all but one has registered udf:s
    server("buffer_exchange_twist_file")
    file_name = "file_name_2"
    file = Path(file_name)
    artifacts = [
        Artifact(lims, id="2-2336703"),
        Artifact(lims, id="2-2336704"),
        Artifact(lims, id="2-2336705"),
        Artifact(lims, id="2-2336706"),
        Artifact(lims, id="2-2336707"),
        Artifact(lims, id="2-2336708"),
    ]

    # WHEN running get_file_data_and_write
    get_file_data_and_write(artifacts, file)

    # THEN the file has been created and missing udfs are replaced with the symbol "-".
    assert file.read_text() == hamilton_buffer_exchange_no_udf
    file.unlink()


def test_get_file_data_and_write_no_well(lims):
    # GIVEN a file name and one artifact which does not have an assigned well
    server("buffer_exchange_twist_file")
    file_name = "file_name_3"
    file = Path(file_name)
    artifacts = [Artifact(lims, id="2-2336715")]

    # WHEN running get_file_data_and_write
    # THEN MissingUDFsError is being raised and no file is created
    with pytest.raises(MissingUDFsError):
        get_file_data_and_write(artifacts, file)
    assert file.exists() is False
