from tests.conftest import server
from pathlib import Path
from cg_lims.exceptions import InvalidValueError, MissingValueError
import pytest

from genologics.entities import Artifact
from cg_lims.EPPs.files.barcode_tubes import get_data_and_write


def test_with_diff_containers(barcode_tubes_csv, lims):
    # GIVEN four artifacts, only two of them ACC9553A3PA1
    # and ACC9621A7PA1 have container type "Tube" and are the
    # only ones to be included in the final file.

    server("hamilton_normalization_file")
    file = Path("file_name_1")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]

    # WHEN running get_data_and_write
    get_data_and_write(artifacts=artifacts, file=file)

    # THEN the file has been created and the file content is as expected.
    file_content = file.read_text()
    file.unlink()
    assert file_content == barcode_tubes_csv


def test_MissingValueError(lims):
    # GIVEN artifacts without container type "Tube".
    server("hamilton_normalization_file")
    file = Path("file_name_2")
    artifacts = [
        Artifact(lims, id="2-2463481"),
        Artifact(lims, id="2-2463482"),
        Artifact(lims, id="2-2463483"),
        Artifact(lims, id="2-2463484"),
        Artifact(lims, id="2-2463485"),
    ]

    # WHEN running get_data_and_write
    with pytest.raises(MissingValueError) as error_message:
        get_data_and_write(artifacts, file=file)

    # Then InvalidValueError exception should be raised, and no file created.
    assert(
        f"Missing samples with container type \"Tube\"."
        in error_message.value.message
    )
    assert file.exists() is False


def test_InvalidValueError(lims):
    # GIVEN artifacts without container type.
    server("flat_tests")
    file = Path("file_name_2")
    artifacts = [
        Artifact(lims, id="1"),
        Artifact(lims, id="2"),
    ]

    # WHEN running get_data_and_write
    with pytest.raises(InvalidValueError) as error_message:
        get_data_and_write(artifacts, file=file)

    # Then InvalidValueError exception should be raised, and no file created.
    assert(
        f"The following samples are missing a container: S1 S1"
        in error_message.value.message
    )
    assert file.exists() is False
