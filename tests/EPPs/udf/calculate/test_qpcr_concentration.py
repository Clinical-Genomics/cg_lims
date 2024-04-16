from pathlib import Path
from typing import List

import click
import pytest
from cg_lims.EPPs.udf.calculate.qpcr_concentration import (
    WellValues,
    calculate_molar_concentration,
    get_index_of_biggest_outlier,
    get_max_difference,
    parse_quantification_summary,
    qpcr_concentration,
)
from cg_lims.exceptions import FileError, MissingFileError
from genologics.entities import Artifact, Process
from tests.conftest import server


@pytest.mark.parametrize(
    "sq_values, size_bp, concentration",
    [
        ([1.10e-12, 1.44e-12, 1.09e-12], 470, 1.1637e-08),
        ([1.41e-12, 1.37e-12, 1.51e-12], 470, 1.3752e-08),
        ([1.37e-12, 1.48e-12, 1.54e-12], 470, 1.4073e-08),
        ([1.34e-12, 1.20e-12, 1.30e-12], 470, 1.231e-08),
    ],
)
def test_calculate_molar_concentration(sq_values: List[float], size_bp: int, concentration: float):
    """Test to verify that molar concentrations are accurately calculated given a set if different SQ values."""
    # GIVEN a set of SQ values of differing values

    # WHEN calculating the molar concentration with calculate_molar_concentration
    result = calculate_molar_concentration(sq_values=sq_values, size_bp=size_bp)

    # THEN the correct value is returned
    assert round(result, 12) == concentration


@pytest.mark.parametrize(
    "values, biggest_index",
    [
        ([1.10e-12, 1.44e-12, 1.09e-12], 1),
        ([10, 7, 6, 8, 5], 0),
        ([0, 100, -100, 123, 454], 4),
        ([-18, -12, -10], 0),
    ],
)
def test_get_index_of_biggest_outlier(values: List[float], biggest_index: int):
    """Test to verify that that the biggest outlier can be identified by the function get_index_of_biggest_outlier"""
    # GIVEN a list of values with differing lengths

    # WHEN running get_index_of_biggest_outlier
    result = get_index_of_biggest_outlier(values=values)

    # THEN the index of the largest entry is returned
    assert result == biggest_index


@pytest.mark.parametrize(
    "values, difference",
    [
        ([1.0e-2, 1.1e-2, 1.2e-2], 0.002),
        ([10, 7, 6, 8, 5], 5),
        ([0, 100, -100, 123, 454], 554),
        ([-18, -12, -10], 8),
    ],
)
def test_get_max_difference(values: List[float], difference: float):
    """Test to verify that the get_max_difference function properly works."""
    # GIVEN a list of values with differing lengths

    # WHEN running get_index_of_biggest_outlier
    result = get_max_difference(values=values)

    # THEN the index of the largest entry is returned
    assert result == difference
