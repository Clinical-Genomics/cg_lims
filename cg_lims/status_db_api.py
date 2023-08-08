import json
import requests
from typing import Any, Dict, List
from urllib.parse import urljoin

from cg_lims.token_manager import TokenManager
from cg_lims.exceptions import LimsError
from cg_lims.models.sample_lane_sequencing_metrics import SampleLaneSequencingMetrics


class StatusDBAPI:
    def __init__(self, base_url: str, token_manager: TokenManager = None) -> None:
        self.base_url: str = base_url
        self._token_manager: TokenManager = token_manager

    @property
    def auth_header(self) -> dict:
        jwt_token: str = self._token_manager.get_token()
        return {"Authorization": f"Bearer {jwt_token}"}

    def _get(self, endpoint: str) -> Any:
        url = self.base_url + endpoint
        try:
            response = requests.get(url, headers=self.auth_header)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LimsError(f"Failed to get data from {url}, {e}")

    def get_application_tag(self, tag_name, key=None, entry_point="/applications"):
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
    ) -> List[SampleLaneSequencingMetrics]:
        metrics_endpoint: str = f"/flowcells/{flow_cell_name}/sequencing_metrics"
        metrics_data: List[Dict] = self._get(metrics_endpoint)
        return [SampleLaneSequencingMetrics.model_validate(metric) for metric in metrics_data]
