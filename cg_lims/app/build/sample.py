from genologics.entities import Sample as GenologicsSample
from cg_lims.get import fields
from cg_lims.models.api.sample import Sample


def build_sample(sample: GenologicsSample) -> Sample:
    sample_udfs = dict(sample.udf.items())
    return Sample(**sample_udfs, id=sample.id, name=sample.name, project=sample.project.id)
