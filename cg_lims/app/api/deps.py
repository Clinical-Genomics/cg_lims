from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD


def get_lims():
    return Lims(BASEURI, USERNAME, PASSWORD)
