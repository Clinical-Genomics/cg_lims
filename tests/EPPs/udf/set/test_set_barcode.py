from re import A
import pytest
from genologics.entities import Artifact, Process

from cg_lims.exceptions import InvalidValueError, MissingValueError
from cg_lims.EPPs.udf.set.set_barcode import get_barcode_set_udf
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server
from cg_lims.get.fields import get_barcode

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



