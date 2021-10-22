import json

import requests

from cg_lims.exceptions import LimsError


class StatusDBAPI(object):
    def __init__(self, url=None):
        self.url = url

    def apptag(self, tag_name, key=None, entry_point="/applications"):
        try:
            res = requests.get(self.url + entry_point + "/" + tag_name)
            if key:
                return json.loads(res.text)[key]
            else:
                return json.loads(res.text)
        except ConnectionError:
            raise LimsError(message="No connection to clinical-api!")
