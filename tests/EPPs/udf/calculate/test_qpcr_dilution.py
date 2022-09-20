from tests.conftest import server
from pathlib import Path
import pytest

from genologics.entities import Artifact
from cg_lims.EPPs.udf.calculate.qpcr_dilution import make_float_list, calculate_and_set_concentrations
from cg_lims.exceptions import FileError, MissingFileError


def test_make_float_list(lims):
    # GIVEN: a string of two float values separated by a comma
    input_string = "0.345,1.670"

    # WHEN using it as input for make_float_list
    output = make_float_list(input_string=input_string)

    # THEN the values are correctly transformed into a list object of two floats
    assert output == [0.345, 1.670]


def test_calculate_and_set_concentrations(qpcr_dilution_file, lims):
    # GIVEN: a set of dilution thresholds, fragment size, a set of input artifacts and an input qPCR
    # dilution file with values corresponding to wells for the input samples.

    server("qpcr_dilution")
    dil_log = Path("dil_log")
    dilution_threshold = 0.4
    d1_dilution_range = [2.5, 5.0]
    d2_dilution_range = [0.7, 1.5]
    dilution_thresholds = [dilution_threshold, d1_dilution_range, d2_dilution_range]
    size_bp = 470
    artifacts = [Artifact(lims=lims, id="92-2753955"),
                 Artifact(lims=lims, id="92-2753956")]

    # WHEN running calculate_and_set_concentrations
    output_message = calculate_and_set_concentrations(
            artifacts=artifacts,
            dilution_file=qpcr_dilution_file,
            dilution_log=dil_log,
            dilution_thresholds=dilution_thresholds,
            size_bp=size_bp
        )

    # THEN the correct output message is returned, artifacts get the correct UDF values and a dilution log is created
    dil_log.unlink()
    assert output_message == "Updated 2 artifact(s), skipped 0 artifact(s) with wrong and/or blank values for" \
                             " some UDFs. WARNING: Removed replicate from 1 samples. See log file for details."
    assert artifacts[0].udf["Concentration (nM)"] == 12.563982525640773
    assert artifacts[1].udf["Concentration (nM)"] == 13.670025686135206


def test_calculate_and_set_concentrations_fail(qpcr_dilution_file_failed, lims):
    # GIVEN: a set of dilution thresholds, fragment size, a set of input artifacts and an input qPCR
    # dilution file where values for one sample is outside the given dilution thresholds.

    server("qpcr_dilution")
    dil_log = Path("dil_log")
    dilution_threshold = 0.4
    d1_dilution_range = [2.5, 5.0]
    d2_dilution_range = [0.7, 1.5]
    dilution_thresholds = [dilution_threshold, d1_dilution_range, d2_dilution_range]
    size_bp = 470
    artifacts = [Artifact(lims=lims, id="92-2753955"),
                 Artifact(lims=lims, id="92-2753956")]

    # WHEN running calculate_and_set_concentrations
    with pytest.raises(FileError) as error_message:
        output_message = calculate_and_set_concentrations(
                artifacts=artifacts,
                dilution_file=qpcr_dilution_file_failed,
                dilution_log=dil_log,
                dilution_thresholds=dilution_thresholds,
                size_bp=size_bp
            )

    # THEN the FileError exception should be raised with the correct message
    dil_log.unlink()
    print(error_message.value.message)
    assert (
            f"Updated 1 artifact(s), skipped 0 artifact(s) with wrong and/or blank values for some UDFs. "
            f"WARNING: Removed replicate from 1 samples. See log file for details. "
            f"WARNING: Failed to set UDFs on 1 samples, due to unstable dilution measurements"
            in error_message.value.message
    )
