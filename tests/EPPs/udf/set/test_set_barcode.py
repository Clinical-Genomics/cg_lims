from concurrent.futures import process
from re import A
import pytest
from genologics.entities import Artifact, Process

from cg_lims.exceptions import InvalidValueError, MissingValueError
from cg_lims.EPPs.udf.set.set_barcode import get_barcode_set_udf
from tests.conftest import server
from cg_lims.get.fields import get_barcode
from cg_lims.get.artifacts import get_artifacts


def test_with_tube(lims):
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
    get_barcode_set_udf(artifacts, barcode_udf, container)

    # THEN only tubes should get barcodes and be correct.
    
    for artifact in artifacts:

        if artifact.container.type.name != container:
            with pytest.raises(KeyError) as e_info:
                artifact.udf[barcode_udf]
        
        else:
            barcode = get_barcode(artifact, container)
            assert artifact.udf[barcode_udf] == barcode


def test_plate_barcode(lims):
    # GIVEN four artifacts, only two of them ACC9551A97PA1
    # and ACC9551A105PA1 have container type '96 well plate' and are the
    # only ones to be included in the final file. None of them
    # have barcode_udf. 

    barcode_udf = 'Output Container Barcode'
    container = '96 well plate'
    server("hamilton_normalization_file")
    artifacts = [
        Artifact(lims, id="ACC9553A3PA1"),
        Artifact(lims, id="ACC9551A97PA1"),
        Artifact(lims, id="ACC9621A7PA1"),
        Artifact(lims, id="ACC9551A105PA1"),
    ]

    # WHEN running get_barcode_set_udf
    with pytest.raises(MissingValueError) as error_message:
        get_barcode_set_udf(artifacts, barcode_udf, container)

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
    get_barcode_set_udf(artifacts, barcode_udf, container)

    # THEN correct barcode should be assigned.
    for artifact in artifacts:        
        barcode = get_barcode(artifact, container)
        assert artifact.udf[barcode_udf] == barcode

def test_InvalidValueError(lims):
    # GIVEN artifacts missing container type.
    server("missing_reads_pool")
    barcode_udf = 'Output Container Barcode'
    container = "Tube"
    artifact = [Artifact(lims, id= "2-1439512")]

    # WHEN running function get_barcode_set_udf.
    with pytest.raises(InvalidValueError) as error_message:
        get_barcode_set_udf(artifact, barcode_udf, container)

    # THEN InvalidValueError should be triggered.
    assert (
        f"Samples ACC7239A44, are missing udf container or udf "
        in error_message.value.message
    )


def test_MissingValueError(lims):
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
        get_barcode_set_udf(artifacts, barcode_udf, container)

    # THEN no barcodes should be assigned and barcode_udf should not 
    # exists.
    assert (
        f"No barcode assigned. Check parameters."
        in error_message.value.message
    )
    
    with pytest.raises(KeyError):
        artifact.udf[barcode_udf]

