import pytest
from genologics.entities import Sample

from cg_lims.exceptions import MissingUDFsError
from cg_lims.get.fields import get_app_tag
from tests.conftest import server

server("flat_tests")


def test_get_app_tag(sample_1: Sample):
    # GIVEN a sample with a udf "Sequencing Analysis"
    sample_1.udf["Sequencing Analysis"] = "TESTAPPTAG"

    # WHEN getting the apptag for that sample
    result = get_app_tag(sample_1)

    # THEN the apptag should be returned
    assert result == "TESTAPPTAG"


def test_get_app_tag_missing_udf(sample_1: Sample):
    # GIVEN a sample with a missing udf "Sequencing Analysis"
    assert sample_1.udf.get("Sequencing Analysis") is None

    # WHEN getting the apptag for that sample
    with pytest.raises(MissingUDFsError) as error_message:
        get_app_tag(sample_1)

    # THEN the correct exception should be raised
    assert (
        f"UDF Sequencing Analysis not found on sample {sample_1.id}"
        in error_message.value.message
    )
