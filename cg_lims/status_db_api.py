import json
from typing import List

import requests

from cg_lims.exceptions import LimsError
from cg_lims.models.api.sequencing_metrics import SequencingMetrics


class StatusDBAPI(object):
    def __init__(self, url):
        self.base_url = url

    def apptag(self, tag_name, key=None, entry_point="/applications"):
        try:
            res = requests.get(self.base_url + entry_point + "/" + tag_name)
            if key:
                return json.loads(res.text)[key]
            else:
                return json.loads(res.text)
        except ConnectionError:
            raise LimsError(message="No connection to clinical-api!")

    def get_sequencing_metrics_for_flow_cell(
        self, flow_cell_name: str
    ) -> List[SequencingMetrics]:
        """
        Retrieves sequencing metrics for a flow cell from the CG API.
        Raises:
            Exception: If the request to the CG API fails.
        """
        metrics_endpoint: str = f"/flowcells/{flow_cell_name}/sequencing_metrics"
        try:
            response = requests.get(self.base_url + metrics_endpoint)
            response.raise_for_status()
            metrics_data = response.json()
            return [SequencingMetrics.model_validate(metric) for metric in metrics_data]
        except requests.RequestException as e:
            raise Exception(f"Failed to get metrics for flowcell {flow_cell_name}, {e}")
