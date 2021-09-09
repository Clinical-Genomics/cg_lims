import logging
from typing import List

from cg_lims.exeptions import InsertError
from pymongo.results import InsertManyResult, InsertOneResult
from cg_lims.adapter import CgLimsAdapter
from cg_lims.models.database import SampleCollection, PrepCollection

LOG = logging.getLogger(__name__)


def create_sample(adapter: CgLimsAdapter, sample: SampleCollection) -> str:
    """Load a sample into the database"""

    sample_dict = sample.dict(exclude_none=True)

    try:
        result: InsertOneResult = adapter.sample_collection.insert_one(sample_dict)
        LOG.info("Added document %s.", sample.sample_id)
    except:
        raise InsertError(message=f"Batch {sample.sample_id} already in database.")
    return result.inserted_id


def create_prep(adapter: CgLimsAdapter, prep: PrepCollection) -> str:
    """Load a prep into the database"""

    prep_dict = prep.dict(exclude_none=True)

    try:
        result: InsertOneResult = adapter.prep_collection.insert_one(prep_dict)
        LOG.info("Added document %s.", prep.prepp_id)
    except:
        raise InsertError(message=f"Batch {prep.prepp_id} already in database.")
    return result.inserted_id


def create_preps(adapter: CgLimsAdapter, preps: List[PrepCollection]) -> List[str]:
    """Load a preps into the database"""

    prep_dicts = []
    for prep in preps:
        prep_dict: dict = prep.dict(exclude_none=True, by_alias=True)
        prep_dicts.append(prep_dict)
    try:
        result: InsertManyResult = adapter.prep_collection.insert_many(prep_dicts)
        LOG.info("Added prep documents.")
    except:
        raise InsertError(f"Prep keys already in database.")
    return result.inserted_ids
