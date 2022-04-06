from tests.conftest import server
from pathlib import Path

from genologics.entities import Artifact
from cg_lims.EPPs.files.hamilton.normalization_file import get_file_data_and_write


def test_make_hamilton_normalization_file(hamilton_normalization_csv, lims):
    # GIVEN: one Aliquot samples for enzymatic fragmentation TWIST v2 process
    # with 7 input artifacts originating from two 96 well plates and two tubes.
    # All samples have been assigned container barcodes in earlier steps, either from
    # reception control or buffer exchange TWIST.

    server("hamilton_normalization_file")
    file = Path("some_file_name")
    artifacts = [
        Artifact(lims, id="2-2463481"),
        Artifact(lims, id="2-2463482"),
        Artifact(lims, id="2-2463483"),
        Artifact(lims, id="2-2463484"),
        Artifact(lims, id="2-2463485"),
        Artifact(lims, id="2-2463486"),
        Artifact(lims, id="2-2463487"),
    ]

    # WHEN running get_file_data_and_write
    get_file_data_and_write(
        pool=False,
        destination_artifacts=artifacts,
        file=file,
        volume_udf="Sample Volume (ul)",
        buffer_udf="Volume H2O (ul)",
    )

    # THEN the file has been created and the file content is as expected.
    file_content = file.read_text()
    file.unlink()
    assert file_content == hamilton_normalization_csv
