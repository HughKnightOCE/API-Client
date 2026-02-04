"""HTTP client for making API requests."""

import json
import requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError


class APIClient:
    """Handles HTTP requests and responses."""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30

    def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request and return the response."""
        try:
            kwargs = {
                "timeout": self.timeout,
            }

            if headers:
                kwargs["headers"] = headers

            if params:
                kwargs["params"] = params

            if body:
                try:
                    kwargs["json"] = json.loads(body)
                except json.JSONDecodeError:
                    # If not JSON, send as raw data
                    kwargs["data"] = body

            response = self.session.request(method.upper(), url, **kwargs)

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": self._parse_response_body(response),
                "success": True,
                "error": None,
            }

        except Timeout:
            return {
                "success": False,
                "error": f"Request timeout after {self.timeout} seconds",
                "status_code": None,
                "headers": {},
                "body": None,
            }
        except ConnectionError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "status_code": None,
                "headers": {},
                "body": None,
            }
        except RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "status_code": None,
                "headers": {},
                "body": None,
            }

    def _parse_response_body(self, response: requests.Response) -> Any:
        """Parse response body as JSON if possible, otherwise return as text."""
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return response.text
