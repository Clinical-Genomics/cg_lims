import requests
from typing import List
from urllib.parse import urljoin

from cg_lims.exceptions import LimsError
from cg_lims.models.sequencing_metrics import SequencingMetrics

class StatusDBAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, endpoint, key=None):
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if key:
                return data.get(key)
            return data
        except requests.RequestException as e:
            raise LimsError(f"Failed to get data from {url}, {e}")

    def apptag(self, tag_name, key=None):
        app_tag_endpoint: str = f"/applications/{tag_name}"
        return self._get(app_tag_endpoint, key)

    def get_sequencing_metrics_for_flow_cell(self, flow_cell_name: str) -> List[SequencingMetrics]:
        metrics_endpoint: str = f"/flowcells/{flow_cell_name}/sequencing_metrics"
        metrics_data = self._get(metrics_endpoint)
        return [SequencingMetrics.model_validate(metric) for metric in metrics_data]
