from cg_lims.exceptions import MissingUDFsError, MissingArtifactError

from pathlib import Path
import json

from cg_lims.EPPs.files.make_kapa_csv import get_file_data_and_write

import pytest


def test_get_file_data_and_write_KAPA_library_preparation(
    lims, kapa_library_preparation_file, helpers, kapa_csv_data
):
    # GIVEN: A file name. and a lims with three samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The tree samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)

    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST"

    helpers.ensure_lims_process(
        lims=lims,
        data={
            "process_type": {"name": amount_step},
            "outputs": kapa_csv_data["amount_artifacts"],
        },
    )
    curent_step_artifacts = helpers.ensure_lims_artifacts(
        lims, kapa_csv_data["artifacts_kapa_library_preparation"]
    )

    file = Path(file_name)

    # WHEN running get_file_data_and_write
    get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)

    # THEN the file has been created and the file content is as expected.
    # See more details in PR:
    # https://github.com/Clinical-Genomics/cg_lims/pull/13#issuecomment-716526239
    assert file.read_text() == kapa_library_preparation_file
    file.unlink()


def test_get_file_data_and_write_Enzymatic_fragmentation(
    lims, enzymatic_fragmentation_file, helpers, kapa_csv_data
):
    # GIVEN: A file name. and a lims with three samples that has been run
    # through a process of type <amount_step>. There  they got udf: Amount needed (ng) set.
    # The tree samples are now in another step where they have location but no
    # reagent labels set.
    # (See entety_json_data for details)

    file_name = "some_file_id"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST"

    helpers.ensure_lims_process(
        lims=lims,
        data={
            "process_type": {"name": amount_step},
            "outputs": kapa_csv_data["amount_artifacts"],
        },
    )
    curent_step_artifacts = helpers.ensure_lims_artifacts(
        lims, kapa_csv_data["artifacts_enzymatic_feragmentation"]
    )

    file = Path(file_name)

    # WHEN running get_file_data_and_write
    get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)

    # THEN the file has been created and the file content is as expected.
    # See more details in PR:
    # https://github.com/Clinical-Genomics/cg_lims/pull/13#issuecomment-716526239
    assert file.read_text() == enzymatic_fragmentation_file
    file.unlink()


def test_get_file_data_and_write_missing_udf(
    lims, kapa_library_preparation_file_missing_udf, helpers, kapa_csv_data
):
    # GIVEN: A file name. and a lims with three samples that has been run
    # through a process of type <amount_step>. There some samples did not get the udf: Amount needed (ng) set.
    # The tree samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)

    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST"

    helpers.ensure_lims_process(
        lims=lims,
        data={
            "process_type": {"name": amount_step},
            "outputs": kapa_csv_data["amount_artifacts_missing_udf"],
        },
    )
    curent_step_artifacts = helpers.ensure_lims_artifacts(
        lims, kapa_csv_data["artifacts_kapa_library_preparation"]
    )

    file = Path(file_name)

    # WHEN running get_file_data_and_write
    # THEN MissingUDFsError is being raised, but the file is still created for the samples that
    # did have the amount udf set.
    with pytest.raises(MissingUDFsError):
        get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)
    assert file.read_text() == kapa_library_preparation_file_missing_udf
    file.unlink()


def test_get_file_data_and_write_missing_artifact(
    lims, kapa_library_preparation_file_missing_udf, helpers, kapa_csv_data
):
    # GIVEN: A file name. and a lims with three samples that has NOT been run
    # through a process of type <amount_step>.
    # The tree samples are now in another step where they have location and
    # reagent labels set.
    # (See entety_json_data for details)

    file_name = "some_file_name"
    amount_step = "Aliquot samples for enzymatic fragmentation TWIST"

    curent_step_artifacts = helpers.ensure_lims_artifacts(
        lims, kapa_csv_data["artifacts_kapa_library_preparation"]
    )

    file = Path(file_name)

    # WHEN running get_file_data_and_write
    # THEN MissingArtifactError is being raised, and no file is being created.
    with pytest.raises(MissingArtifactError):
        get_file_data_and_write(lims, amount_step, curent_step_artifacts, file)
    assert file.exists() == False
