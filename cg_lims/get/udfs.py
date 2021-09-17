from genologics.lims import Lims
from typing import Optional
from datetime import date
import logging

from cg_lims.exceptions import MissingArtifactError
from cg_lims.get.artifacts import get_latest_artifact

LOG = logging.getLogger(__name__)


def get_udf_type(lims: Lims, udf_name: str, attach_to_name: str) -> Optional:
    """Get udf type.

    Args:
        udf_name:
            eg: 'Concentration (nM)', 'Comment',...
        attach_to_name: name of entity to which the udf is attached
            eg. 'ResultFile', 'Analyte', 'Aggregate QC (RNA)',...
    """
    udf_types = {"String": str, "Numeric": float, "Date": date}

    udf_configs = lims.get_udfs(name=udf_name, attach_to_name=attach_to_name)
    udf_configs[0].get()
    udf_type = udf_configs[0].root.attrib["type"]

    return udf_types[udf_type]


def filter_process_udfs_by_model(lims: Lims, sample_id: str, process_type: str, model):
    """"""
    try:
        artifact = get_latest_artifact(lims=lims, sample_id=sample_id, process_type=[process_type])
    except MissingArtifactError as e:
        LOG.info(e.message)
        return dict()
    process_udfs = dict(artifact.parent_process.udf.items())
    udf_model = model(**process_udfs)
    return udf_model.dict(exclude_none=True)


def filter_process_artifact_udfs_by_model(
    lims: Lims, sample_id: str, process_type: str, model
) -> dict:
    """"""
    try:
        artifact = get_latest_artifact(lims=lims, sample_id=sample_id, process_type=[process_type])
    except MissingArtifactError as e:
        LOG.info(e.message)
        return dict()
    artifact_udfs = dict(artifact.udf.items())
    udf_model = model(**artifact_udfs)
    return udf_model.dict(exclude_none=True)
