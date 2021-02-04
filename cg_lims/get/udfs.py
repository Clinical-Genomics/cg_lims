from genologics.lims import Lims
from typing import Optional
from datetime import date


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
