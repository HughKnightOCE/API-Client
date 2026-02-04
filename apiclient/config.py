"""Configuration management for API client."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel


class RequestConfig(BaseModel):
    """Configuration for a saved request."""

    name: str
    method: str
    url: str
    headers: Dict[str, str] = {}
    body: Optional[str] = None
    params: Dict[str, str] = {}

    class Config:
        json_encoders = {
            Path: str,
        }


class Config:
    """Manages application configuration and storage."""

    def __init__(self):
        self.config_dir = Path.home() / ".apiclient"
        self.requests_file = self.config_dir / "requests.json"
        self.history_file = self.config_dir / "history.json"
        self.ensure_config_dir()

    def ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)

    def load_requests(self) -> Dict[str, RequestConfig]:
        """Load saved requests from file."""
        if not self.requests_file.exists():
            return {}

        try:
            with open(self.requests_file, "r") as f:
                data = json.load(f)
                return {
                    name: RequestConfig(**config) for name, config in data.items()
                }
        except (json.JSONDecodeError, ValueError):
            return {}

    def save_request(self, config: RequestConfig):
        """Save a request configuration."""
        requests = self.load_requests()
        requests[config.name] = config

        with open(self.requests_file, "w") as f:
            json.dump(
                {name: req.dict() for name, req in requests.items()},
                f,
                indent=2,
            )

    def delete_request(self, name: str) -> bool:
        """Delete a saved request."""
        requests = self.load_requests()
        if name in requests:
            del requests[name]
            with open(self.requests_file, "w") as f:
                json.dump(
                    {n: req.dict() for n, req in requests.items()},
                    f,
                    indent=2,
                )
            return True
        return False

    def get_request(self, name: str) -> Optional[RequestConfig]:
        """Get a specific saved request."""
        requests = self.load_requests()
        return requests.get(name)

    def add_to_history(self, method: str, url: str):
        """Add a request to history."""
        history = self.load_history()
        entry = {"method": method, "url": url}

        if entry not in history:
            history.append(entry)
            # Keep only last 50
            history = history[-50:]

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)

    def load_history(self) -> list:
        """Load request history."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []
