from genologics.entities import Sample as GenologicsSample
from cg_lims.get import fields
from cg_lims.app.schemas.sample import Sample


def build_sample(sample: GenologicsSample) -> Sample:

    return Sample(
        id=sample.id,
        name=sample.name,
        project=sample.project.id,
        comment=fields.get_sample_comment(sample),
        received_date=fields.get_received_date(sample),
        prepared_date=fields.get_prepared_date(sample),
        sequenced_date=fields.get_sequenced_date(sample),
        delivery_date=fields.get_delivery_date(sample),
        processing_time=fields.get_processing_time(sample),
    )
