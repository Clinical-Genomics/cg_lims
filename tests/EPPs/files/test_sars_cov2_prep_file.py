from genologics.entities import Process

from cg_lims.get.artifacts import get_artifacts
from tests.conftest import server
from pathlib import Path

from cg_lims.EPPs.files.hamilton.sars_cov2_prep_file import get_file_data_and_write


def test_make_hamilton_sars_cov2_pooling_file(hamilton_sars_cov2_pooling_file, lims):
    # GIVEN: A file name. and a lims with samples that has been run
    # through a pooling step with id 122-194650.

    server("hamilton_sars_cov2_pooling_step")
    file = Path("some_file_name")
    process = Process(lims, id="122-194650")
    artifacts = get_artifacts(process=process)

    # WHEN running get_file_data_and_write
    get_file_data_and_write(pool=True, file=file, destination_artifacts=artifacts)

    # THEN the file has been created and the file content is as expected.
    file_content = file.read_text()
    file.unlink()
    assert file_content == hamilton_sars_cov2_pooling_file


def test_make_hamilton_sars_cov2_indexing_file(hamilton_sars_cov2_indexing_file, lims):
    # GIVEN: A file name. and a lims with samples that has been run
    # through a indexing step with id 151-196204.

    server("hamilton_sars_cov2_indexing_step")
    file = Path("some_file_name")
    process = Process(lims, id="151-196204")
    artifacts = get_artifacts(process=process, input=False)

    # WHEN running get_file_data_and_write
    get_file_data_and_write(pool=False, file=file, destination_artifacts=artifacts)

    # THEN the file has been created and the file content is as expected.
    file_content = file.read_text()
    file.unlink()
    assert file_content == hamilton_sars_cov2_indexing_file
