import json
import logging
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests

from cg_lims.exceptions import LimsError
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics

LOG = logging.getLogger(__name__)

class StatusDBAPI:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _get(self, endpoint: str) -> Any:
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.ConnectionError:
            LOG.error(f"Connection error when accessing {url}")
            raise LimsError(f"Failed to connect to the server at {url}.")

        except requests.Timeout:
            LOG.error(f"Timeout error when accessing {url}")
            raise LimsError(f"Request to {url} timed out.")

        except requests.RequestException as e:
            LOG.error(f"Error when accessing {url}: {e}")
            raise LimsError(f"An error occurred while making the request to {url}: {e}.")

        except json.JSONDecodeError:
            LOG.error(f"Failed to decode JSON from {url}")
            raise LimsError(f"Received an invalid JSON response from {url}.")
            

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
