from tests.conftest import server
from pathlib import Path

from genologics.entities import Artifact

import pytest

from cg_lims.EPPs.files.hamilton.make_kapa_csv import get_file_data_and_write
from cg_lims.exceptions import MissingArtifactError, MissingUDFsError


def test_get_file_data_and_write_KAPA_library_preparation(kapa_library_preparation_file, lims):
    # GIVEN: A file name. and a lims with two samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The two samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)
    server("test_make_kapa_csv")
    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST v2"
    file = Path(file_name)
    curent_step_artifacts = [Artifact(lims, id="2-1155129"), Artifact(lims, id="2-1155130")]

    # WHEN running get_file_data_and_write
    get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)

    # THEN the file has been created and the file content is as expected.
    # See more details in PR:
    # https://github.com/Clinical-Genomics/cg_lims/pull/13#issuecomment-716526239
    assert file.read_text() == kapa_library_preparation_file
    file.unlink()


def test_get_file_data_and_write_Enzymatic_fragmentation(enzymatic_fragmentation_file, lims):
    # GIVEN: A file name. and a lims with two samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The two samples are now in another step where they have location but no
    # reagent labels set.
    # (See entety_json_data for details)
    server("test_make_kapa_csv")
    file_name = "some_file_id"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST v2"
    file = Path(file_name)
    curent_step_artifacts = [Artifact(lims, id="2-1155124"), Artifact(lims, id="2-1155125")]

    # WHEN running get_file_data_and_write
    get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)

    # THEN the file has been created and the file content is as expected.
    # See more details in PR:
    # https://github.com/Clinical-Genomics/cg_lims/pull/13#issuecomment-716526239
    assert file.read_text() == enzymatic_fragmentation_file
    file.unlink()


def test_get_file_data_and_write_missing_udf(kapa_library_preparation_file_missing_udf, lims):
    # GIVEN: A file name. and a lims with two samples that has been run
    # through a process of type <amount_step>. There one sample did not get the udf: Amount needed (ng) set.
    # The two samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)
    server("make_kapa_csv_missing_udfs")
    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST v2"
    file = Path(file_name)
    curent_step_artifacts = [Artifact(lims, id="2-1155129"), Artifact(lims, id="2-1155130")]

    # WHEN running get_file_data_and_write
    # THEN MissingUDFsError is being raised, but the file is still created for the sample that
    # did have the amount udf set.
    with pytest.raises(MissingUDFsError):
        get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)
    assert file.read_text() == kapa_library_preparation_file_missing_udf
    file.unlink()


def test_get_file_data_and_write_missing_artifact(kapa_library_preparation_file_missing_udf, lims):
    # GIVEN: A file name. and a lims with two samples that has NOT been run
    # through a process of type <amount_step>.
    # The two samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)
    server("make_kapa_csv_missing_udfs")
    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST v2"
    file = Path(file_name)
    curent_step_artifacts = [
        Artifact(lims, id="2-1155129_other_sample"),
        Artifact(lims, id="2-1155130_other_sample"),
    ]

    # WHEN running get_file_data_and_write
    # THEN MissingArtifactError is being raised, and no file is being created.
    with pytest.raises(MissingArtifactError):
        get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)
    assert file.exists() == False
