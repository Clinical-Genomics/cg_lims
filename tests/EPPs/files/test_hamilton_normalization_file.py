from tests.conftest import server
from pathlib import Path

from genologics.entities import Artifact, Process
from cg_lims.EPPs.files.hamilton.normalization_file import get_file_data_and_write
from cg_lims.get.artifacts import get_artifacts


def test_make_hamilton_normalization_file(hamilton_normalization_file, lims):
    # GIVEN: A file name. and a lims with two samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The two samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)

    server("hamilton_normalization_file")
    file = Path("some_file_name")
    process = Process(lims, id="24-315081")
    artifacts = get_artifacts(process=process, input=True)
    artifacts_alternative = [
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
        Artifact(lims, id="ACC9551A113PA1"),
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="2-2463328"),
        Artifact(lims, id="2-2463329"),
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
