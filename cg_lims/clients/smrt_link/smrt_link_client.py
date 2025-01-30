#!/usr/bin/env python3

# Copyright (c) 2023, Pacific Biosciences of California, Inc.
##
# All rights reserved.
##
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of Pacific Biosciences nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
##
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE.  THIS SOFTWARE IS PROVIDED BY PACIFIC BIOSCIENCES AND ITS
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PACIFIC BIOSCIENCES OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
SMRT Link REST API reference client implementation, for version 12.0.0
or newer.  This is written to be self-contained without any
dependencies on internal PacBio libraries, and can be copied, modified, and
redistributed without limitation (see module comments for license terms).

The SmrtLinkClient does not cover the entire API, but the code is intended to
be easily extended and translated into other languages.  For simplicity and
readability, the returned objects are weakly typed lists
and dicts containing basic Python types (str, int, float, bool, None).
The Swagger documentation in the SMRT Link GUI online help
(https://servername:8243/sl/docs/services) provides a comprehensive listing
of endpoints and data models.

Note: This module has been modified and shortened down significantly from the source material available on
GitHub https://github.com/PacificBiosciences/pbcommand/blob/develop/pbcommand/services/smrtlink_client.py

"""

import json
import logging
from abc import ABC, abstractmethod

import requests

__all__ = [
    "SmrtLinkClient",
]

log = logging.getLogger(__name__)


class Constants:
    API_PORT = 8243
    H_CT_AUTH = "application/x-www-form-urlencoded"
    H_CT_JSON = "application/json"
    # SSL is good and we should not disable it by default
    DEFAULT_VERIFY = True


def refresh_on_401(f):
    """
    Method decorator to trigger a token refresh when an HTTP 401 error is
    received.
    """

    def wrapper(self, *args, **kwds):
        try:
            return f(self, *args, **kwds)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.refresh()
                return f(self, *args, **kwds)
            else:
                raise

    return wrapper


def _disable_insecure_warning():
    """
    Workaround to silence SSL warnings when the invoker has explicitly
    requested insecure mode.
    """
    import warnings

    # To disable the ssl cert check warning
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning  # pylint: disable=import-error

    urllib3.disable_warnings(InsecureRequestWarning)  # pylint: disable=no-member


class RESTClient(ABC):
    """
    Base class for interacting with any REST API that communicates primarily
    in JSON.
    """

    PROTOCOL = "http"

    def __init__(self, host, port, verify=Constants.DEFAULT_VERIFY):
        self.host = host
        self.port = port
        self._verify = verify

    @abstractmethod
    def refresh(self): ...

    @property
    def headers(self):
        return {"Content-Type": Constants.H_CT_JSON}

    @property
    def base_url(self):
        return f"{self.PROTOCOL}://{self.host}:{self.port}"

    def to_url(self, path):
        """Convert an API method path to the full server URL"""
        return f"{self.base_url}{path}"

    def _get_headers(self, other_headers={}):
        headers = dict(self.headers)
        if other_headers:
            headers.update(other_headers)
        return headers

    @refresh_on_401
    def _http_get(self, path, params=None, headers={}):
        if isinstance(params, dict):
            if len(params) == 0:
                params = None
            else:
                # get rid of queryParam=None elements
                params = {k: v for k, v in params.items() if v is not None}
        url = self.to_url(path)
        log.info(f"Method: GET {path}")
        log.debug(f"Full URL: {url}")
        response = requests.get(
            url, params=params, headers=self._get_headers(headers), verify=self._verify
        )
        log.debug(response)
        response.raise_for_status()
        return response

    @refresh_on_401
    def _http_post(self, path, data, headers={}):
        url = self.to_url(path)
        log.info(f"Method: POST {path} {data}")
        log.debug(f"Full URL: {url}")
        response = requests.post(
            url, data=json.dumps(data), headers=self._get_headers(headers), verify=self._verify
        )
        log.debug(response)
        response.raise_for_status()
        return response

    @refresh_on_401
    def _http_put(self, path, data, headers={}):
        url = self.to_url(path)
        log.info(f"Method: PUT {path} {data}")
        log.debug(f"Full URL: {url}")
        response = requests.put(
            url, data=json.dumps(data), headers=self._get_headers(headers), verify=self._verify
        )
        log.debug(response)
        response.raise_for_status()
        return response

    @refresh_on_401
    def _http_delete(self, path, headers={}):
        url = self.to_url(path)
        log.info(f"Method: DELETE {path}")
        log.debug(f"Full URL: {url}")
        response = requests.delete(url, headers=self._get_headers(headers), verify=self._verify)
        log.debug(response)
        response.raise_for_status()
        return response

    @refresh_on_401
    def _http_options(self, path, headers={}):
        url = self.to_url(path)
        log.info(f"Method: OPTIONS {url}")
        log.debug(f"Full URL: {url}")
        response = requests.options(url, headers=self._get_headers(headers), verify=self._verify)
        log.debug(response)
        response.raise_for_status()
        return response

    def get(self, path, params=None, headers={}):
        """Generic JSON GET method handler"""
        return self._http_get(path, params, headers).json()

    def post(self, path, data, headers={}):
        """Generic JSON POST method handler"""
        return self._http_post(path, data, headers).json()

    def put(self, path, data, headers={}):
        """Generic JSON PUT method handler"""
        return self._http_put(path, data, headers).json()

    def delete(self, path, headers={}):
        """Generic JSON DELETE method handler"""
        return self._http_delete(path, headers).json()

    def options(self, path, headers={}):
        """
        OPTIONS handler, used only for getting CORS settings in ReactJS.
        Since the response body is empty, the return value is the response
        headers (as a dict).
        """
        return self._http_options(path, headers).headers()

    def execute_call(self, method, path, data, headers):
        """Execute any supported JSON-returning HTTP call by name"""
        if method == "GET":
            return self.get(path, headers=headers)
        elif method == "POST":
            return self.post(path, data=data, headers=headers)
        elif method == "PUT":
            return self.put(path, data=data, headers=headers)
        elif method == "DELETE":
            return self.get(path, headers=headers)
        elif method == "OPTIONS":
            return self.options(path, headers=headers)
        else:
            raise ValueError(f"Method '{method}' not supported")


class AuthenticatedClient(RESTClient):
    """
    Base class for REST clients that require authorization via the Oauth2
    token interface.
    """

    def __init__(self, host, port, username, password, verify=Constants.DEFAULT_VERIFY):
        super(AuthenticatedClient, self).__init__(host, port, verify)
        self._user = username
        self._oauth2 = self.get_authorization_token(username, password)

    @property
    def auth_token(self):
        return self._oauth2["access_token"]

    @property
    def refresh_token(self):
        return self._oauth2["refresh_token"]

    @property
    def headers(self):
        """Dict of default HTTP headers for all endpoints"""
        return {"Content-Type": Constants.H_CT_JSON, "Authorization": f"Bearer {self.auth_token}"}

    @abstractmethod
    def get_authorization_token(self, username, password): ...


class SmrtLinkClient(AuthenticatedClient):
    """
    Class for executing methods on the secure (authenticated) SMRT Link REST
    API, via API gateway
    """

    PROTOCOL = "https"
    JOBS_PATH = "/smrt-link/job-manager/jobs"

    def __init__(self, *args, **kwds):
        if not kwds.get("verify", Constants.DEFAULT_VERIFY):
            _disable_insecure_warning()
        super(SmrtLinkClient, self).__init__(*args, **kwds)

    @staticmethod
    def connect(host, username, password, verify=Constants.DEFAULT_VERIFY):
        """
        Convenience method for instantiating a client using the default
        API port 8243
        """
        return SmrtLinkClient(
            host=host, port=Constants.API_PORT, username=username, password=password, verify=verify
        )

    @property
    def headers(self):
        return {
            "Content-Type": Constants.H_CT_JSON,
            "Authorization": f"Bearer {self.auth_token}",
            "X-User-ID": self._user,
        }

    def to_url(self, path):
        return f"{self.base_url}/SMRTLink/2.0.0{path}"

    def get_authorization_token(self, username, password):
        """
        Request an Oauth2 authorization token from the SMRT Link API
        server, which is actually a proxy to Keycloak.  This token will
        enable access to all API methods that are allowed for the role of
        the authorized user.
        """
        auth_d = dict(username=username, password=password, grant_type="password")
        resp = requests.post(
            f"{self.base_url}/token",
            data=auth_d,
            headers={"Content-Type": Constants.H_CT_AUTH},
            verify=self._verify,
        )
        resp.raise_for_status()
        t = resp.json()
        log.info("Access token: {}...".format(t["access_token"][0:40]))
        log.debug("Access token: {}".format(t["access_token"]))
        return t

    def refresh(self):
        """
        Attempt to refresh the authorization token, using the refresh token
        obtained in a previous request.
        """
        log.info("Requesting new access token using refresh token")
        auth_d = dict(grant_type="refresh_token", refresh_token=self.refresh_token)
        resp = requests.post(
            self.to_url("/token"),
            data=auth_d,
            headers={"Content-Type": Constants.H_CT_AUTH},
            verify=self._verify,
        )
        resp.raise_for_status()
        t = resp.json()
        log.info("Access token: {}...".format(t["access_token"][0:40]))
        log.debug("Access token: {}".format(t["access_token"]))
        self._oauth2 = t
        return t

    # -----------------------------------------------------------------
    # RUNS
    def get_runs(self, **search_params):
        """
        Get a list of all PacBio instrument runs, with optional search
        parameters.

        Partial list of supported search parameters:
            name (partial matches supported)
            reserved (boolean, true means selected on instrument)
            instrumentType (Revio, Sequel2e, or Sequel2)
            chipType (8mChip or 25mChip)
            collectionUuid (retrieve the run for a specific collection)
            movieName
        """
        return self.get("/smrt-link/runs", dict(search_params))

    def get_run(self, run_id):
        """Retrieve a PacBio instrument run description by UUID"""
        return self.get(f"/smrt-link/runs/{run_id}")

    def get_run_qc(self, run_id):
        """Retrieve a PacBio instrument run QC description by UUID"""
        return self.get(f"/smrt-link/runs/{run_id}/qc")

    def get_run_xml(self, run_id):
        """
        Retrieve the XML data model for a PacBio instrument run
        """
        return self._http_get(f"/smrt-link/runs/{run_id}/datamodel").text

    def get_run_collections(self, run_id):
        """Retrieve a list of collections/samples for a run"""
        return self.get(f"/smrt-link/runs/{run_id}/collections")

    def get_run_collection(self, run_id, collection_id):
        """Retrieve metadata for a single collection in a run"""
        return self.get(f"/smrt-link/runs/{run_id}/collections/{collection_id}")

    def get_run_from_collection_id(self, collection_id):
        """
        Convenience method wrapping get_runs(), for retrieving a run based
        on collection UUID alone.  Returns None if no matching run is found.
        """
        runs = self.get_runs(collectionUuid=collection_id)
        return None if len(runs) == 0 else runs[0]

    def get_run_collection_reports(self, run_id, collection_id):
        """
        Get all reports associated with a run collection
        Introduced in SMRT Link 13.0
        """
        return self.get(f"/smrt-link/runs/{run_id}/collections/{collection_id}/reports")

    def get_run_collection_barcodes(self, run_id, collection_id):
        """Get a list of barcoded samples associated with a run collection"""
        return self.get(f"/smrt-link/runs/{run_id}/collections/{collection_id}/barcodes")

    def get_run_collection_hifi_reads(self, run_id, collection_id):
        """
        Retrieve the HiFi dataset that is the primary output of a PacBio
        instrument run.
        """
        collection = self.get_run_collection(run_id, collection_id)
        return self.get_consensusreadset(collection["ccsId"])

    def get_run_collection_hifi_reads_barcoded_datasets(
        self, run_id, collection_id, barcode_name=None, biosample_name=None
    ):
        """
        Retrieve the demultiplexed "child" datasets for a PacBio instrument
        run, optionally filtering by barcode name (e.g. 'bc2001--bc2001') or
        biosample name.
        """
        collection = self.get_run_collection(run_id, collection_id)
        return self.get_barcoded_child_datasets(
            collection["ccsId"], barcode_name=barcode_name, biosample_name=biosample_name
        )

    def get_run_reports(self, run_id):
        """
        Get all collection-level reports associated with a run.
        Introduced in SMRT Link 13.0
        """
        return self.get(f"/smrt-link/runs/{run_id}/reports")

    def get_run_design(self, run_id):
        """Return the run design JSON object used by the SMRT Link GUI"""
        return self.get(f"/smrt-link/run-design/{run_id}")

    def import_run_design_csv(self, csv_file):
        """
        Import a Run CSV definition and return the run-design data model.
        This is the officially supported interface for creating a Run Design
        programatically.
        """
        csv_d = {"content": open(csv_file, "rt").read()}
        return self.post("/smrt-link/import-run-design", csv_d)

    def delete_run(self, run_id):
        """Delete a PacBio run description by UUID"""
        return self.delete(f"/smrt-link/runs/{run_id}")

    def import_run_xml(self, xml_file):
        """
        Post a Run XML directly to the API.  This is not officially supported
        as an integration mechanism, but is useful for transferring Run QC
        results between servers.
        """
        return self.post("/smrt-link/runs", {"dataModel": open(xml_file).read()})

    def update_run_xml(self, xml_file, run_id, is_reserved=None):
        """
        Update a Run data model XML.  This endpoint is what the Revio and Sequel
        II/IIe instruments use to communicate run progress, and to mark a run
        as "reserved" by a particular instrument.  It can be used as a workaround
        for updating the status of incomplete runs after manual XML edits.
        """
        opts_d = {"dataModel": open(xml_file).read()}
        if is_reserved is not None:
            opts_d["reserved"] = is_reserved
        return self.post(f"/smrt-link/runs/{run_id}", opts_d)

    # -----------------------------------------------------------------
    # DATASETS
    def _get_datasets_by_type(self, dataset_type, **query_args):
        return self.get(f"/smrt-link/datasets/{dataset_type}", params=dict(query_args))

    def _get_dataset_by_type_and_id(self, dataset_type, dataset_id):
        return self.get(f"/smrt-link/datasets/{dataset_type}/{dataset_id}")

    def _get_dataset_resources_by_type_and_id(self, dataset_type, dataset_id, resource_type):
        return self.get(f"/smrt-link/datasets/{dataset_type}/{dataset_id}/{resource_type}")

    def get_consensusreadsets(self, **query_args):
        """
        Retrieve a list of HiFi datasets, with optional search parameters.
        Partial list of supported search terms:
            name
            bioSampleName
            wellSampleName
            metadataContextId (movie name)
        String searches are always case-insensitive.
        Most of the non-timestamp string fields in the data model are
        searchable with partial strings by adding the prefix 'like:' to the
        search term, thus:
            client.get_consensusreadsets(bioSampleName="like:HG002")
        The refixes 'not:' (inequality), 'unlike:', 'start:', and 'end:' are
        also recognized.  For numerical fields, 'not:', 'lt:', 'lte:', 'gt:',
        'gte:' are supported, plus 'range:{start},{end}'.
        """
        return self._get_datasets_by_type("ccsreads", **query_args)

    def get_consensusreadsets_by_movie(self, movie_name):
        """
        Retrieve a list of HiFi datasets for a unique movie name (AKA
        'context' or 'metadataContextId'), such as 'm84001_230601_123456'
        """
        return self.get_consensusreadsets(metadataContextId=movie_name)

    def get_barcoded_child_datasets(
        self, parent_dataset_id, barcode_name=None, biosample_name=None
    ):
        """Get a list of demultiplexed children (if any) of a HiFi dataset"""
        return self.get_consensusreadsets(
            parentUuid=parent_dataset_id, dnaBarcodeName=barcode_name, bioSampleName=biosample_name
        )

    def get_subreadsets(self, **query_args):
        """
        Retrieve a list of CLR/subread datasets, with optional search
        parameters. (DEPRECATED)
        """
        return self._get_datasets_by_type("subreads", **query_args)

    def get_referencesets(self, **query_args):
        """Get a list of ReferenceSet datasets"""
        return self._get_datasets_by_type("references", **query_args)

    def get_barcodesets(self, **query_args):
        """Get a list of BarcodeSet datasets (including MAS-Seq adapters and Iso-Seq primers)"""
        return self._get_datasets_by_type("barcodes", **query_args)

    def get_consensusreadset(self, dataset_id):
        """Get a HiFi dataset by UUID or integer ID"""
        return self._get_dataset_by_type_and_id("ccsreads", dataset_id)

    def get_subreadset(self, dataset_id):
        """Get a CLR (subread) dataset by UUID or integer ID (DEPRECATED)"""
        return self._get_dataset_by_type_and_id("subreads", dataset_id)

    def get_referenceset(self, dataset_id):
        """GET /smrt-link/datasets/references/{dataset_id}"""
        return self._get_dataset_by_type_and_id("references", dataset_id)

    def get_barcodeset(self, dataset_id):
        """GET /smrt-link/datasets/barcodes/{dataset_id}"""
        return self._get_dataset_by_type_and_id("barcodes", dataset_id)

    def get_consensusreadset_reports(self, dataset_id):
        """Get a list of reports associated with a HiFi dataset"""
        return self._get_dataset_resources_by_type_and_id("ccsreads", dataset_id, "reports")

    def get_barcodeset_contents(self, dataset_id):
        """
        Retrieve the entire contents of a BarcodeSet dataset, as a
        raw FASTA string (not JSON!)
        """
        path = f"/smrt-link/datasets/barcodes/{dataset_id}/contents"
        return self._http_get(path).text

    def get_barcodeset_record_names(self, dataset_id):
        """Retrieve a list of barcode/primer/adapter names in a BarcodeSet"""
        return self._get_dataset_resources_by_type_and_id("barcodes", dataset_id, "record-names")

    def get_dataset_metadata(self, dataset_id):
        """Retrieve a type-independent dataset metadata object"""
        return self._get_dataset_by_type_and_id("meta", dataset_id)

    def get_dataset_jobs(self, dataset_id):
        """Get a list of analysis jobs that used the specified dataset as input"""
        return self._get_dataset_resources_by_type_and_id("meta", dataset_id, "jobs")

    def get_dataset_search(self, dataset_id):
        """
        Retrieve a single dataset if it is present in the database, or None
        if it is missing, without triggering an HTTP 404 error in the latter
        case.
        """
        result_d = self.get(f"/smrt-link/datasets/search/{dataset_id}")
        if not result_d:  # empty dict is the "not found" response
            return None
        return result_d
