from tests.conftest import server
from pathlib import Path

from genologics.entities import Artifact
from cg_lims.EPPs.files.hamilton.normalization_file import get_file_data_and_write


def test_make_hamilton_normalization_file(hamilton_normalization_file, lims):
    # GIVEN: A file name. and a lims with two samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The two samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)

    server("make_hamilton_normalization_file")
    file = Path("some_file_name")
    artifacts = [
        Artifact(lims, id="2-1450827"),
        Artifact(lims, id="2-1450824"),
        Artifact(lims, id="2-1450825"),
        Artifact(lims, id="2-1450826"),
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
    assert file_content == hamilton_normalization_file
