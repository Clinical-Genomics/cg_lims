import json

import requests


class StatusDBAPI(object):
    def __init__(self, url=None):
        self.url = url

    def apptag(self, tag_name, key=None, entry_point="/applications"):
        res = requests.get(self.url + entry_point + "/" + tag_name)
        if key:
            return json.loads(res.text)[key]
        else:
            return json.loads(res.text)
