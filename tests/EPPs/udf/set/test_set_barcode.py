import imp
import pytest
from genologics.entities import Artifact, Process

from cg_lims.exceptions import InvalidValueError, MissingValueError
from cg_lims.EPPs.udf.set.set_barcode import get_barcode_set_udf
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server