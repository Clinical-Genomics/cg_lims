import mock
import pytest
from genologics.entities import Sample

from cg_lims.EPPs.udf.set.set_samples_reads_missing import (
    get_app_tag,
    get_target_amount,
    set_reads_missing,
    set_reads_missing_on_sample,
)
from cg_lims.exceptions import LimsError, MissingUDFsError
from tests.conftest import server


@mock.patch("cg_lims.status_db_api.StatusDBAPI")
@mock.patch("cg_lims.EPPs.udf.set.set_samples_reads_missing.get_target_amount")
@mock.patch("cg_lims.EPPs.udf.set.set_samples_reads_missing.get_app_tag")
def test_set_reads_missing_on_sample(
    mock_get_app_tag, mock_get_target_amount, mock_status_db, sample_1: Sample
):
    """ """
    server("flat_tests")

    # GIVEN A SAMPLE
    sample = sample_1

    # WHEN setting the missing reads on that sample_1
    mock_get_target_amount.return_value = 9_000_000

    set_reads_missing_on_sample(sample_1, mock_status_db)

    # THEN the udf "Reads missing (M)" on that sample should be set
    assert sample_1.udf["Reads missing (M)"] == 9


def test_get_app_tag(sample_1: Sample):
    """ """
    # GIVEN a sample with a udf "Sequencing Analysis"
    sample_1.udf["Sequencing Analysis"] = "TESTAPPTAG"

    # WHEN getting the apptag for that sample
    result = get_app_tag(sample_1)

    # THEN the apptag should be returned
    assert result == "TESTAPPTAG"


def test_get_app_tag_missing_udf(sample_1: Sample):
    """ """
    # GIVEN a sample with a missing udf "Sequencing Analysis"

    # WHEN getting the apptag for that sample
    with pytest.raises(MissingUDFsError) as error_message:
        get_app_tag(sample_1)

    # THEN
    assert (
        f"UDF Sequencing Analysis not found on sample {sample_1.id}"
        in error_message.value.message
    )


@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_get_target_amount(mock_status_db):
    """ """
    # GIVEN an apptag
    apptag = "TESTAPPTAG"

    # WHEN fetching the target amount
    mock_status_db.apptag.return_value = 9_000_000
    result = get_target_amount(apptag, mock_status_db)

    # THEN the correct value should be returned
    assert result == 9_000_000


@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_get_target_amount_connection_error(mock_status_db):
    """ """
    # GIVEN a connection error
    apptag = "TESTAPPTAG"
    mock_status_db.apptag.side_effect = ConnectionError

    # WHEN fetching the target amount
    with pytest.raises(LimsError) as error_message:
        get_target_amount(apptag, mock_status_db)

    # THEN
    assert f"No connection to clinical-api!" in error_message.value.message


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_one_sample(
    mock_status_db, mock_set_reads_missing_on_sample, sample_1: Sample
):
    """ """

    # GIVEN a single sample
    samples = [sample_1]

    # WHEN setting the reads missing on those samples
    result = set_reads_missing(samples, status_db=mock_status_db)

    # THEN
    mock_set_reads_missing_on_sample.assert_called_with(sample_1, mock_status_db)
    assert result == 0


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_multiple_samples(
    mock_status_db, mock_set_reads_missing_on_sample, sample_1: Sample, sample_2: Sample
):
    """ """

    # GIVEN a list of samples
    samples = [sample_1, sample_2]

    # WHEN setting the reads missing on those samples
    result = set_reads_missing(samples, status_db=mock_status_db)

    # THEN the missing reads should be set on both samples
    assert mock_set_reads_missing_on_sample.call_count == 2
    mock_set_reads_missing_on_sample.assert_has_calls(
        [
            mock.call(sample_1, mock_status_db),
            mock.call(sample_2, mock_status_db),
        ]
    )
    assert mock_set_reads_missing_on_sample.mock_calls == [
        mock.call(sample_1, mock_status_db),
        mock.call(sample_2, mock_status_db),
    ]
    assert result == 0


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_one_sample_exception(
    mock_status_db, mock_set_reads_missing_on_sample, sample_1: Sample
):
    """ """

    # GIVEN a single sample
    samples = [sample_1]
    mock_set_reads_missing_on_sample.side_effect = Exception

    # WHEN setting the reads missing on those samples
    with pytest.raises(Exception):
        result = set_reads_missing(samples, mock_status_db)

    # THEN
    mock_set_reads_missing_on_sample.assert_called_with(sample_1, mock_status_db)
    assert result == 1
