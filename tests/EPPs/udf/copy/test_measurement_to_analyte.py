import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.copy.measurement_to_analyte import copy_udfs_to_all_analytes
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte
from cg_lims.exceptions import MissingUDFsError
from tests.conftest import server


def test_copy_udf(lims):
    # GIVEN a Reception control WGS process with sample measurements which are connected to analytes, measurements
    # have barcodes stored in UDF "Output Container Barcode"
    server("reception_control_wgs")
    process = Process(lims, id="24-349794")
    measurements = get_artifacts(process=process, measurement=True)
    analytes = get_artifacts(process=process, input=True)
    barcodes = {
        "ACC10237A2": "barcode1",
        "ACC10242A8": "barcode2",
        "ACC10243A1": "barcode3",
    }
    udfs = [("Output Container Barcode", "Output Container Barcode")]
    for measurement in measurements:
        measurement.udf["Output Container Barcode"] = barcodes[measurement.samples[0].id]

    # WHEN running copy_udfs_to_all_analytes to copy the barcodes
    copy_udfs_to_all_analytes(
        measurements=measurements,
        udfs=udfs,
    )

    # THEN the correct source UDFs are copied over to the correct analytes
    for analyte in analytes:
        assert analyte.udf["Output Container Barcode"] == barcodes[analyte.samples[0].id]


def test_copy_udf_missing_udfs(lims):
    # GIVEN a Reception control WGS process with sample measurements which are connected to analytes, measurements
    # don't have values stored in the required UDF
    server("reception_control_wgs")
    process = Process(lims, id="24-349794")
    measurements = get_artifacts(process=process, measurement=True)
    udfs = [("Output Container Barcode", "Output Container Barcode")]

    # WHEN when running copy_udfs_to_all_analytes
    # THEN MissingUDFsError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        copy_udfs_to_all_analytes(
            measurements=measurements,
            udfs=udfs,
        )
