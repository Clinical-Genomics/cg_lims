import json
import requests

from cg_lims.token_manager import TokenManager
from cg_lims.exceptions import LimsError


class StatusDBAPI:
    def __init__(self, url: str, token_manager: TokenManager = None):
        self.url: str = url
        self._token_manager: TokenManager = token_manager

    def apptag(self, tag_name, key=None, entry_point="/applications"):
        try:
            res = requests.get(self.url + entry_point + "/" + tag_name)
            if key:
                return json.loads(res.text)[key]
            else:
                return json.loads(res.text)
        except ConnectionError:
            raise LimsError(message="No connection to clinical-api!")
