import logging
from cg_lims.adapter import CgLimsAdapter
from cg_lims.models.database import SampleCollection, PrepCollection
LOG = logging.getLogger(__name__)


def update_sample(adapter: CgLimsAdapter, sample: SampleCollection) -> None:
    """Update a sample object in the database"""

    sample_dict: dict = sample.dict(exclude_none=True)
    LOG.info("Updating sample %s", sample.sample_id)
    adapter.sample_collection.update_one({"sample_id": sample.sample_id}, {"$set": sample_dict})


def update_prep(adapter: CgLimsAdapter, prep: PrepCollection) -> None:
    """Update a prep object in the database"""

    prep_dict: dict = prep.dict(exclude_none=True)
    LOG.info("Updating sample %s", prep.prepp_id)
    adapter.sample_collection.update_one({"sample_id": prep.prepp_id}, {"$set": prep_dict})

