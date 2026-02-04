"""Configuration management for API client."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class Assertion(BaseModel):
    """Response assertion for validation."""
    field: str  # e.g., "status" or "response.data.id"
    operator: str  # "equals", "contains", "greater_than", "less_than", "exists"
    expected: Any


class RequestConfig(BaseModel):
    """Configuration for a saved request."""

    name: str
    method: str
    url: str
    headers: Dict[str, str] = {}
    body: Optional[str] = None
    params: Dict[str, str] = {}
    collection: Optional[str] = None  # Folder/collection name
    assertions: List[Assertion] = []  # Response validations
    tags: List[str] = []  # For organization

    class Config:
        json_encoders = {
            Path: str,
        }


class Environment(BaseModel):
    """Environment variables for request substitution."""
    name: str
    variables: Dict[str, str] = {}  # e.g., {"API_KEY": "sk-123", "BASE_URL": "https://api.example.com"}


class Collection(BaseModel):
    """Request collection/folder."""
    name: str
    description: Optional[str] = None
    requests: List[str] = []  # List of request names in this collection
    parent: Optional[str] = None  # For nested collections


class Config:
    """Manages application configuration and storage."""

    def __init__(self):
        self.config_dir = Path.home() / ".apiclient"
        self.requests_file = self.config_dir / "requests.json"
        self.history_file = self.config_dir / "history.json"
        self.environments_file = self.config_dir / "environments.json"
        self.collections_file = self.config_dir / "collections.json"
        self.ensure_config_dir()

    def ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)

    # ==================== REQUESTS ====================
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

    # ==================== ENVIRONMENTS ====================
    def load_environments(self) -> Dict[str, Environment]:
        """Load environment variables."""
        if not self.environments_file.exists():
            return {}

        try:
            with open(self.environments_file, "r") as f:
                data = json.load(f)
                return {name: Environment(**env) for name, env in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}

    def save_environment(self, env: Environment):
        """Save environment variables."""
        environments = self.load_environments()
        environments[env.name] = env

        with open(self.environments_file, "w") as f:
            json.dump(
                {name: e.dict() for name, e in environments.items()},
                f,
                indent=2,
            )

    def delete_environment(self, name: str) -> bool:
        """Delete an environment."""
        environments = self.load_environments()
        if name in environments:
            del environments[name]
            with open(self.environments_file, "w") as f:
                json.dump(
                    {n: e.dict() for n, e in environments.items()},
                    f,
                    indent=2,
                )
            return True
        return False

    def get_environment(self, name: str) -> Optional[Environment]:
        """Get specific environment."""
        environments = self.load_environments()
        return environments.get(name)

    # ==================== COLLECTIONS ====================
    def load_collections(self) -> Dict[str, Collection]:
        """Load request collections."""
        if not self.collections_file.exists():
            return {}

        try:
            with open(self.collections_file, "r") as f:
                data = json.load(f)
                return {name: Collection(**coll) for name, coll in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}

    def save_collection(self, collection: Collection):
        """Save a collection."""
        collections = self.load_collections()
        collections[collection.name] = collection

        with open(self.collections_file, "w") as f:
            json.dump(
                {name: c.dict() for name, c in collections.items()},
                f,
                indent=2,
            )

    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        collections = self.load_collections()
        if name in collections:
            del collections[name]
            with open(self.collections_file, "w") as f:
                json.dump(
                    {n: c.dict() for n, c in collections.items()},
                    f,
                    indent=2,
                )
            return True
        return False

    def get_collection(self, name: str) -> Optional[Collection]:
        """Get specific collection."""
        collections = self.load_collections()
        return collections.get(name)

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
