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


class RequestChain(BaseModel):
    """Chain of requests to execute sequentially."""
    name: str
    description: Optional[str] = None
    requests: List[str] = []  # List of request names in order
    extract_rules: List[Dict[str, Any]] = []  # Variable extraction rules
    # Example: [{"from_request": 0, "response_path": "data.id", "variable_name": "USER_ID"}]


class RequestTemplate(BaseModel):
    """Reusable request template."""
    name: str
    category: str  # "REST", "GraphQL", "gRPC", etc.
    description: Optional[str] = None
    base_url: str
    method: str
    headers: Dict[str, str] = {}
    body: Optional[str] = None
    params: Dict[str, str] = {}
    default_environment: Optional[str] = None
    example_response: Optional[Dict[str, Any]] = None
    tags: List[str] = []


class PerformanceMetric(BaseModel):
    """Performance metric for a request."""
    request_name: str
    status_code: int
    response_time: float  # in seconds
    timestamp: str  # ISO format
    request_size: Optional[int] = None  # bytes
    response_size: Optional[int] = None  # bytes


class AuthenticationConfig(BaseModel):
    """Authentication configuration."""
    name: str
    type: str  # "api_key", "basic", "bearer", "oauth2", "jwt"
    config: Dict[str, Any] = {}  # Type-specific config
    # API Key: {"header_name": "X-API-Key", "key": "value"}
    # Basic: {"username": "...", "password": "..."}
    # Bearer: {"token": "..."}
    # OAuth2: {"client_id": "...", "client_secret": "...", "auth_url": "...", "token_url": "..."}
    # JWT: {"secret": "...", "algorithm": "HS256", "payload": {...}}


class MockEndpoint(BaseModel):
    """Mock HTTP endpoint."""
    name: str
    method: str  # GET, POST, etc.
    path: str  # /api/users, /api/posts/:id, etc.
    status_code: int = 200
    response: Dict[str, Any] = {}
    delay_ms: int = 0  # Response delay in milliseconds
    headers: Dict[str, str] = {}


class GraphQLQuery(BaseModel):
    """GraphQL query definition."""
    name: str
    endpoint: str
    query: str  # GraphQL query text
    variables: Dict[str, Any] = {}
    operation_name: Optional[str] = None
    headers: Dict[str, str] = {}


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

    # ==================== CHAINS ====================
    def load_chains(self) -> Dict[str, RequestChain]:
        """Load request chains."""
        chains_file = self.config_dir / "chains.json"
        if not chains_file.exists():
            return {}
        
        try:
            with open(chains_file, "r") as f:
                data = json.load(f)
                return {name: RequestChain(**config) for name, config in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def save_chain(self, chain: RequestChain):
        """Save a request chain."""
        chains_file = self.config_dir / "chains.json"
        chains = self.load_chains()
        chains[chain.name] = chain
        
        with open(chains_file, "w") as f:
            json.dump({name: c.dict() for name, c in chains.items()}, f, indent=2)
    
    def delete_chain(self, name: str) -> bool:
        """Delete a request chain."""
        chains_file = self.config_dir / "chains.json"
        chains = self.load_chains()
        if name in chains:
            del chains[name]
            with open(chains_file, "w") as f:
                json.dump({n: c.dict() for n, c in chains.items()}, f, indent=2)
            return True
        return False

    # ==================== TEMPLATES ====================
    def load_templates(self) -> Dict[str, RequestTemplate]:
        """Load request templates."""
        templates_file = self.config_dir / "templates.json"
        if not templates_file.exists():
            return {}
        
        try:
            with open(templates_file, "r") as f:
                data = json.load(f)
                return {name: RequestTemplate(**config) for name, config in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def save_template(self, template: RequestTemplate):
        """Save a request template."""
        templates_file = self.config_dir / "templates.json"
        templates = self.load_templates()
        templates[template.name] = template
        
        with open(templates_file, "w") as f:
            json.dump({name: t.dict() for name, t in templates.items()}, f, indent=2)
    
    def delete_template(self, name: str) -> bool:
        """Delete a request template."""
        templates_file = self.config_dir / "templates.json"
        templates = self.load_templates()
        if name in templates:
            del templates[name]
            with open(templates_file, "w") as f:
                json.dump({n: t.dict() for n, t in templates.items()}, f, indent=2)
            return True
        return False

    # ==================== METRICS ====================
    def load_metrics(self) -> List[PerformanceMetric]:
        """Load performance metrics."""
        metrics_file = self.config_dir / "metrics.json"
        if not metrics_file.exists():
            return []
        
        try:
            with open(metrics_file, "r") as f:
                data = json.load(f)
                return [PerformanceMetric(**m) for m in data]
        except (json.JSONDecodeError, ValueError):
            return []
    
    def save_metric(self, metric: PerformanceMetric):
        """Save a performance metric."""
        metrics_file = self.config_dir / "metrics.json"
        metrics = self.load_metrics()
        metrics.append(metric)
        # Keep only last 1000
        metrics = metrics[-1000:]
        
        with open(metrics_file, "w") as f:
            json.dump([m.dict() for m in metrics], f, indent=2)

    # ==================== AUTH ====================
    def load_auth_configs(self) -> Dict[str, AuthenticationConfig]:
        """Load authentication configurations."""
        auth_file = self.config_dir / "auth.json"
        if not auth_file.exists():
            return {}
        
        try:
            with open(auth_file, "r") as f:
                data = json.load(f)
                return {name: AuthenticationConfig(**config) for name, config in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def save_auth_config(self, auth: AuthenticationConfig):
        """Save authentication configuration."""
        auth_file = self.config_dir / "auth.json"
        configs = self.load_auth_configs()
        configs[auth.name] = auth
        
        with open(auth_file, "w") as f:
            json.dump({name: c.dict() for name, c in configs.items()}, f, indent=2)
    
    def delete_auth_config(self, name: str) -> bool:
        """Delete authentication configuration."""
        auth_file = self.config_dir / "auth.json"
        configs = self.load_auth_configs()
        if name in configs:
            del configs[name]
            with open(auth_file, "w") as f:
                json.dump({n: c.dict() for n, c in configs.items()}, f, indent=2)
            return True
        return False

    # ==================== MOCK ENDPOINTS ====================
    def load_mock_endpoints(self) -> Dict[str, MockEndpoint]:
        """Load mock endpoints."""
        mocks_file = self.config_dir / "mocks.json"
        if not mocks_file.exists():
            return {}
        
        try:
            with open(mocks_file, "r") as f:
                data = json.load(f)
                return {name: MockEndpoint(**config) for name, config in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def save_mock_endpoint(self, endpoint: MockEndpoint):
        """Save mock endpoint."""
        mocks_file = self.config_dir / "mocks.json"
        endpoints = self.load_mock_endpoints()
        endpoints[endpoint.name] = endpoint
        
        with open(mocks_file, "w") as f:
            json.dump({name: e.dict() for name, e in endpoints.items()}, f, indent=2)
    
    def delete_mock_endpoint(self, name: str) -> bool:
        """Delete mock endpoint."""
        mocks_file = self.config_dir / "mocks.json"
        endpoints = self.load_mock_endpoints()
        if name in endpoints:
            del endpoints[name]
            with open(mocks_file, "w") as f:
                json.dump({n: e.dict() for n, e in endpoints.items()}, f, indent=2)
            return True
        return False

    # ==================== GRAPHQL ====================
    def load_graphql_queries(self) -> Dict[str, GraphQLQuery]:
        """Load GraphQL queries."""
        graphql_file = self.config_dir / "graphql.json"
        if not graphql_file.exists():
            return {}
        
        try:
            with open(graphql_file, "r") as f:
                data = json.load(f)
                return {name: GraphQLQuery(**config) for name, config in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def save_graphql_query(self, query: GraphQLQuery):
        """Save GraphQL query."""
        graphql_file = self.config_dir / "graphql.json"
        queries = self.load_graphql_queries()
        queries[query.name] = query
        
        with open(graphql_file, "w") as f:
            json.dump({name: q.dict() for name, q in queries.items()}, f, indent=2)
    
    def delete_graphql_query(self, name: str) -> bool:
        """Delete GraphQL query."""
        graphql_file = self.config_dir / "graphql.json"
        queries = self.load_graphql_queries()
        if name in queries:
            del queries[name]
            with open(graphql_file, "w") as f:
                json.dump({n: q.dict() for n, q in queries.items()}, f, indent=2)
            return True
        return False
