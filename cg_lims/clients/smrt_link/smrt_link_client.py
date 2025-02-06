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

    def import_run_design_csv(self, csv_file):
        """
        Import a Run CSV definition and return the run-design data model.
        This is the officially supported interface for creating a Run Design
        programatically.
        """
        csv_d = {"content": open(csv_file, "rt").read()}
        return self.post("/smrt-link/import-run-design", csv_d)
