import mock
import pytest
from genologics.entities import Sample

from cg_lims.EPPs.udf.set.set_samples_reads_missing import (
    get_target_amount,
    set_reads_missing,
    set_reads_missing_on_sample,
)
from cg_lims.exceptions import LimsError, MissingUDFsError
from tests.conftest import server


@mock.patch("cg_lims.get.udfs.get_udf")
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_get_target_amount(mock_status_db, mock_get_udf, sample_1: Sample):
    # GIVEN a sample with a udf "Sequencing Analysis" containing an app
    # tag
    server("flat_tests")
    test_app_tag = "TESTAPPTAG"
    sample_1.udf["Sequencing Analysis"] = test_app_tag

    # WHEN getting the target amount of reads via the StatusDBAPI
    mock_get_udf.return_value = test_app_tag
    mock_status_db.apptag.return_value = 9_000_000
    result = get_target_amount(test_app_tag, mock_status_db)

    # THEN the target amount of reads should be retrieved via the StatusDBAPI
    assert result == 9_000_000
    assert mock_status_db.apptag.mock_calls == [
        mock.call(tag_name=test_app_tag, key="target_reads")
    ]


@mock.patch("cg_lims.status_db_api.StatusDBAPI")
@mock.patch("cg_lims.EPPs.udf.set.set_samples_reads_missing.get_target_amount")
@mock.patch("cg_lims.EPPs.udf.set.set_samples_reads_missing.get_udf")
def test_set_reads_missing_on_sample(
    mock_get_udf,
    mock_get_target_amount,
    mock_status_db,
    sample_1: Sample,
):
    # GIVEN A SAMPLE
    sample = sample_1

    # WHEN setting the missing reads on that sample_1 based on the target amount
    mock_get_target_amount.return_value = 9_000_000

    set_reads_missing_on_sample(sample, mock_status_db)

    # THEN the udf "Reads missing (M)" on that sample should be set correctly
    assert sample.udf["Reads missing (M)"] == 9


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_one_sample(
    mock_status_db, mock_set_reads_missing_on_sample, sample_1: Sample
):
    # GIVEN a single sample
    samples = [sample_1]

    # WHEN setting the reads missing on that sample
    set_reads_missing(samples, status_db=mock_status_db)

    # THEN set_missing_reads should be called for that sample
    mock_set_reads_missing_on_sample.assert_called_with(sample_1, mock_status_db)


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_multiple_samples(
    mock_status_db, mock_set_reads_missing_on_sample, sample_1: Sample, sample_2: Sample
):
    # GIVEN multiple of samples
    samples = [sample_1, sample_2]

    # WHEN setting the reads missing on those samples
    set_reads_missing(samples, status_db=mock_status_db)

    # THEN the missing reads should be set on both samples
    assert mock_set_reads_missing_on_sample.mock_calls == [
        mock.call(sample_1, mock_status_db),
        mock.call(sample_2, mock_status_db),
    ]


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_one_sample_exception(
    mock_status_db,
    mock_set_reads_missing_on_sample,
    sample_1: Sample,
):
    # GIVEN a single sample
    samples = [sample_1]

    # WHEN setting the reads missing on that sample leads to an exception  being raised
    mock_set_reads_missing_on_sample.side_effect = MissingUDFsError("TEST MISSING UDF")
    with pytest.raises(LimsError) as error:
        set_reads_missing(samples, mock_status_db)

    # AND one failed sample should be counted, and it's id should be returned
    mock_set_reads_missing_on_sample.assert_called_with(sample_1, mock_status_db)
    assert (
        error.value.message
        == "Reads Missing (M) set on 0 sample(s), 1 sample(s) failed"
    )


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_multiple_samples_exception_on_first_sample(
    mock_status_db,
    mock_set_reads_missing_on_sample,
    sample_1: Sample,
    sample_2: Sample,
):
    # GIVEN multiple samples
    samples = [sample_1, sample_2]

    # WHEN setting the reads missing on those samples and the second sample leads to an exception being raised
    mock_set_reads_missing_on_sample.side_effect = (
        None,
        MissingUDFsError("TEST MISSING UDF"),
    )
    with pytest.raises(LimsError) as error:
        set_reads_missing(samples, mock_status_db)

    # THEN setting the missing reads should be attempted for both samples
    assert mock_set_reads_missing_on_sample.mock_calls == [
        mock.call(sample_1, mock_status_db),
        mock.call(sample_2, mock_status_db),
    ]
    # AND one failed sample should be counted, and it's id should be returned
    assert (
        error.value.message
        == "Reads Missing (M) set on 1 sample(s), 1 sample(s) failed"
    )


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_multiple_samples_exception_on_second_sample(
    mock_status_db,
    mock_set_reads_missing_on_sample,
    sample_1: Sample,
    sample_2: Sample,
):
    # GIVEN multiple samples
    samples = [sample_1, sample_2]
    assert sample_1.udf.get("Sequencing Analysis") is None

    # WHEN setting the reads missing on those samples and the first sample leads to an exception being raised

    mock_set_reads_missing_on_sample.side_effect = (
        MissingUDFsError("TEST MISSING UDF"),
        None,
    )
    with pytest.raises(LimsError) as error:
        set_reads_missing(samples, mock_status_db)

    # THEN setting the missing reads should be attempted for both samples
    assert mock_set_reads_missing_on_sample.mock_calls == [
        mock.call(sample_1, mock_status_db),
        mock.call(sample_2, mock_status_db),
    ]
    # AND one failed sample should be counted
    assert (
        error.value.message
        == "Reads Missing (M) set on 1 sample(s), 1 sample(s) failed"
    )


@mock.patch(
    "cg_lims.EPPs.udf.set.set_samples_reads_missing.set_reads_missing_on_sample"
)
@mock.patch("cg_lims.status_db_api.StatusDBAPI")
def test_set_reads_missing_multiple_samples_exception_on_both_samples(
    mock_status_db,
    mock_set_reads_missing_on_sample,
    sample_1: Sample,
    sample_2: Sample,
):
    # GIVEN multiple samples
    samples = [sample_1, sample_2]
    assert sample_1.udf.get("Sequencing Analysis") is None

    # WHEN setting the reads missing on those samples and both samples leads to an exception being raised
    mock_set_reads_missing_on_sample.side_effect = (
        MissingUDFsError("TEST MISSING UDF"),
        MissingUDFsError("TEST MISSING UDF"),
    )
    with pytest.raises(LimsError) as error:
        set_reads_missing(samples, mock_status_db)

    # THEN setting the missing reads should be attempted for both samples
    assert mock_set_reads_missing_on_sample.mock_calls == [
        mock.call(sample_1, mock_status_db),
        mock.call(sample_2, mock_status_db),
    ]
    # AND two failed sample should be counted, and their id's should be returned
    assert (
        error.value.message
        == "Reads Missing (M) set on 0 sample(s), 2 sample(s) failed"
    )
