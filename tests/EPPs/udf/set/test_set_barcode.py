import pytest

from genologics.entities import Artifact, Process
from cg_lims.exceptions import InvalidValueError, MissingValueError
from cg_lims.EPPs.udf.set.set_barcode import get_barcode_set_udf
from cg_lims.get.fields import get_barcode
from cg_lims.get.artifacts import get_artifacts
from tests.conftest import server


def test_tube_barcode(lims):
    # GIVEN four artifacts, only two of them ACC9553A3PA1
    # and ACC9621A7PA1 have container type "Tube" and are the
    # only ones to be have assigned a barcode udf.

    barcode_udf = 'Output Container Barcode'
    container = 'Tube'
    server("hamilton_normalization_file")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]

    for artifact in artifacts:
        del artifact.udf[barcode_udf]

    # WHEN running get_barcode_set_udf
    get_barcode_set_udf(artifacts=artifacts, artifact_udf=barcode_udf, container_type=container, measurement=False)

    # THEN only tubes should get barcodes and be correct.
    for artifact in artifacts:
        if artifact.container.type.name != container:
            with pytest.raises(KeyError) as e_info:
                artifact.udf[barcode_udf]
        else:
            barcode = get_barcode(artifact)
            assert artifact.udf[barcode_udf] == barcode


def test_plate_barcode(lims):
    # GIVEN four artifacts, only two of them ACC9551A97PA1
    # and ACC9551A105PA1 have container type '96 well plate' and are the
    # only ones to be included in the final file. None of them
    # have barcode_udf. 

    barcode_udf = 'Output Container Barcode'
    container = 'Some container name'
    server("hamilton_normalization_file")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]

    # WHEN running get_barcode_set_udf
    with pytest.raises(MissingValueError) as error_message:
        get_barcode_set_udf(artifacts=artifacts, artifact_udf=barcode_udf, container_type=container, measurement=False)

    # THEN InvalidValueError exception should be raised.
    # Because plate barcode has no specific barcode.
    assert(
        f"No barcode assigned."
        in error_message.value.message
    )


def test_pool_barcode(lims):
    # GIVEN artifacts with multiple samples - a pool -
    # and container type 'Tube'.
    server("pool_samples_TWIST")
    barcode_udf = 'Output Container Barcode'
    container = 'Tube'
    process = Process(lims, id="122-202801")
    artifacts = get_artifacts(process=process, input=False)
    
    for artifact in artifacts:
        if len(artifact.samples) == 1:
            exit()

    # WHEN running function get_barcode_set_udf.
    get_barcode_set_udf(artifacts=artifacts, artifact_udf=barcode_udf, container_type=container, measurement=False)

    # THEN correct barcode should be assigned.
    for artifact in artifacts:        
        barcode = get_barcode(artifact)
        assert artifact.udf[barcode_udf] == barcode


def test_no_container_type(lims):
    # GIVEN four artifacts, two of them (ACC9553A3PA1
    # and ACC9621A7PA1) have container type "Tube" and
    # the other two (ACC9551A97PA1 and ACC9551A105PA1)
    # belong to a "96 well plate" container

    barcode_udf = 'Output Container Barcode'
    server("hamilton_normalization_file")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]

    for artifact in artifacts:
        del artifact.udf[barcode_udf]

    # WHEN running get_barcode_set_udf
    get_barcode_set_udf(artifacts=artifacts, artifact_udf=barcode_udf, container_type="", measurement=False)

    # THEN all artifacts should get barcodes and be correct.
    for artifact in artifacts:
        barcode = get_barcode(artifact)
        assert artifact.udf[barcode_udf] == barcode


def test_invalid_value(lims):
    # GIVEN artifacts missing container type.
    server("missing_reads_pool")
    barcode_udf = 'Output Container Barcode'
    container = "Tube"
    artifact = [Artifact(lims, id="2-1439512")]

    # WHEN running function get_barcode_set_udf.
    with pytest.raises(InvalidValueError) as error_message:
        get_barcode_set_udf(artifacts=artifact, artifact_udf=barcode_udf, container_type=container, measurement=False)

    # THEN InvalidValueError should be triggered.
    assert (
        f"Samples ACC7239A44, are missing udf container or udf "
        in error_message.value.message
    )


def test_missing_value(lims):
    # GIVEN two artifacts, with container "Tube"
    # and container set to "No_tubes".
    barcode_udf = 'Output Container Barcode'
    container = 'No_tubes'
    server("hamilton_normalization_file")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
    ]

    for artifact in artifacts:
        del artifact.udf[barcode_udf]

    # WHEN running function get_barcode_set_udf.
    with pytest.raises(MissingValueError) as error_message:
        get_barcode_set_udf(artifacts=artifacts, artifact_udf=barcode_udf, container_type=container, measurement=False)

    # THEN no barcodes should be assigned and barcode_udf should not 
    # exists.
    assert (
        f"No barcode assigned. Check parameters."
        in error_message.value.message
    )
    
    with pytest.raises(KeyError):
        artifact.udf[barcode_udf]


def test_container_on_measurement(lims):
    # GIVEN measurements with different containers.
    barcode_udf = 'Output Container Barcode'
    container = 'Tube'
    server("reception_control_wgs")
    process = Process(lims, id="24-349794")
    measurements = get_artifacts(process=process, measurement=True)

    for measurement in measurements:
        try:
            del measurement.udf[barcode_udf]
        except:
            continue

    # WHEN running get_barcode_set_udf
    get_barcode_set_udf(artifacts=measurements, artifact_udf=barcode_udf, container_type=container, measurement=True)

    # THEN barcodes should be assigned on measurement level only to samples with correct container.
    for measurement in measurements:
        if measurement.samples[0].artifact.container.type.name != container:
            with pytest.raises(KeyError):
                measurement.udf[barcode_udf]
        
        else:
            barcode = get_barcode(measurement.samples[0].artifact)
            assert measurement.udf[barcode_udf] == barcode


def test_missing_value_on_measurement(lims):
    # GIVEN measurements with different containers.
    barcode_udf = 'Output Container Barcode'
    container = 'foobar'
    server("reception_control_wgs")
    process = Process(lims, id="24-349794")
    measurements = get_artifacts(process=process, measurement=True)

    for measurement in measurements:
        try:
            del measurement.udf[barcode_udf]
        except:
            continue

    # WHEN running function get_barcode_set_udf.
    with pytest.raises(MissingValueError) as error_message:
        get_barcode_set_udf(artifacts=measurements, artifact_udf=barcode_udf, container_type=container, measurement=True)

    # THEN no barcodes should be assigned and barcode_udf should not 
    # exists.
    assert (
        f"No barcode assigned. Check parameters."
        in error_message.value.message
    )
    
    with pytest.raises(KeyError):
        measurement.udf[barcode_udf]
