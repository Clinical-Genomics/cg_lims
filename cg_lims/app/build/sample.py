from cg_lims.app import lims
from genologics.entities import Sample
from cg_lims.get import fields


def build_sample(sample_id: str):
    genologics_sample = Sample(lims, id=sample_id)
    udfs = genologics_sample.udf

    sample = {
        "id": sample_id,
        "name": genologics_sample.name,
        "project": genologics_sample.project.id,
        "comment": fields.get_sample_comment(genologics_sample),
        "received_date": fields.get_received_date(genologics_sample),
        "prepared_date": fields.get_prepared_date(genologics_sample),
        "sequenced_date": fields.get_sequenced_date(genologics_sample),
        "delivery_date": fields.get_delivery_date(genologics_sample),
        "processing_time": fields.get_processing_time(genologics_sample),
    }
    return sample
