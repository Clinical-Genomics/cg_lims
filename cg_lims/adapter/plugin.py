import logging

from mongo_adapter import MongoAdapter
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

LOG = logging.getLogger(__name__)


class CgLimsAdapter(MongoAdapter):
    def setup(self, db_name: str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db: Database = self.client[db_name]
        self.db_name: str = db_name
        self.sample_collection: Collection = self.db.sample
        self.prep_collection: Collection = self.db.prep
        self.sequencing_collection: Collection = self.db.sequencing

        LOG.info("Use database %s.", db_name)


def get_cg_lims_adapter(db_uri, db_name):
    client = MongoClient(db_uri)
    return CgLimsAdapter(client, db_name=db_name)
