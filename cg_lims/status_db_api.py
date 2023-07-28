import requests
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from cg_lims.exceptions import LimsError
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics


class StatusDBAPI:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _get(self, endpoint: str) -> Any:
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LimsError(f"Failed to get data from {url}, {e}")

    def apptag(self, tag_name: str, key: Optional[str] = None):
        app_tag_endpoint: str = f"/applications/{tag_name}"
        data: Dict = self._get(app_tag_endpoint)
        if key:
            return data.get(key)
        return data

    def get_sequencing_metrics_for_flow_cell(
        self, flow_cell_name: str
    ) -> List[SampleLaneSequencingMetrics]:
        metrics_endpoint: str = f"/flowcells/{flow_cell_name}/sequencing_metrics"
        metrics_data: List[Dict] = self._get(metrics_endpoint)
        return [SampleLaneSequencingMetrics.model_validate(metric) for metric in metrics_data]
