import logging
from cg_lims.exeptions import InsertError
from pymongo.results import InsertOneResult
from cg_lims.adapter import CgLimsAdapter
from cg_lims.models.database import SampleCollection, PrepCollection

LOG = logging.getLogger(__name__)


def insert_sample(adapter: CgLimsAdapter, sample: SampleCollection) -> str:
    """Load a sample into the database"""

    sample_dict = sample.dict(exclude_none=True)

    try:
        result: InsertOneResult = adapter.sample_collection.insert_one(sample_dict)
        LOG.info("Added document %s.", sample.sample_id)
    except:
        raise InsertError(message=f"Batch {sample.sample_id} already in database.")
    return result.inserted_id


def insert_prep(adapter: CgLimsAdapter, prep: PrepCollection) -> str:
    """Load a prep into the database"""

    prep_dict = prep.dict(exclude_none=True)

    try:
        result: InsertOneResult = adapter.prep_collection.insert_one(prep_dict)
        LOG.info("Added document %s.", prep.prepp_id)
    except:
        raise InsertError(message=f"Batch {prep.prepp_id} already in database.")
    return result.inserted_id
