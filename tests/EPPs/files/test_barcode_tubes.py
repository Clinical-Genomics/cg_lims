from tests.conftest import server
from pathlib import Path
import pytest

from genologics.entities import Artifact
from cg_lims.EPPs.files.barcode_tubes import get_data_and_write

def test_with_tubes(barcode_tubes_csv, lims):
    # GIVEN: artifacts with different containers.

    server("hamilton_normalization_file")
    file = Path("file_name_1")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]
    
    # WHEN running get_data_and_write
    get_data_and_write(artifacts, file=file)

    # THEN the file has been created and the file content is as expected.
    file_content = file.read_text()
    file.unlink()
    assert file_content == barcode_tubes_csv
