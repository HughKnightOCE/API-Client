"""
Phase 3: Authentication Helpers, Mock Server, GraphQL Support
"""

import json
import jwt
import base64
import requests
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import subprocess
import os
import signal


class AuthenticationManager:
    """Manage various authentication methods: API Key, OAuth2, JWT."""
    
    @staticmethod
    def generate_api_key_header(api_key: str, header_name: str = "X-API-Key") -> Dict[str, str]:
        """Generate API key authentication header."""
        return {header_name: api_key}
    
    @staticmethod
    def generate_basic_auth(username: str, password: str) -> Dict[str, str]:
        """Generate HTTP Basic authentication header."""
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {"Authorization": f"Basic {credentials}"}
    
    @staticmethod
    def generate_bearer_token_header(token: str) -> Dict[str, str]:
        """Generate Bearer token authentication header."""
        return {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    def generate_oauth2_authorization_url(client_id: str, redirect_uri: str, 
                                         auth_url: str, scope: str = "") -> str:
        """Generate OAuth2 authorization URL."""
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": secrets.token_urlsafe(32)
        }
        return f"{auth_url}?{urlencode(params)}"
    
    @staticmethod
    def exchange_oauth2_code(code: str, client_id: str, client_secret: str,
                            redirect_uri: str, token_url: str) -> Dict[str, Any]:
        """Exchange OAuth2 authorization code for access token."""
        data = {
            "grant_type": "code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def generate_jwt(payload: Dict[str, Any], secret: str, algorithm: str = "HS256",
                    expires_in_hours: int = 24) -> str:
        """Generate a JWT token."""
        payload_with_exp = payload.copy()
        payload_with_exp["exp"] = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        try:
            token = jwt.encode(payload_with_exp, secret, algorithm=algorithm)
            return token if isinstance(token, str) else token.decode()
        except Exception as e:
            raise Exception(f"Error generating JWT: {str(e)}")
    
    @staticmethod
    def verify_jwt(token: str, secret: str, algorithm: str = "HS256") -> Tuple[bool, Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return False, {"error": str(e)}
    
    @staticmethod
    def decode_jwt_without_verification(token: str) -> Dict[str, Any]:
        """Decode JWT without verification (for inspection)."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return {"error": "Invalid JWT format"}
            
            # Decode payload (add padding if needed)
            payload_part = parts[1]
            padding = 4 - len(payload_part) % 4
            if padding != 4:
                payload_part += "=" * padding
            
            payload = json.loads(base64.urlsafe_b64decode(payload_part))
            return payload
        except Exception as e:
            return {"error": str(e)}


class MockServerManager:
    """Manage mock HTTP server for testing."""
    
    mock_process = None
    mock_endpoints = {}
    
    @staticmethod
    def start_mock_server(port: int = 9000) -> bool:
        """Start mock HTTP server."""
        try:
            mock_app_code = f'''
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

mock_endpoints = {json.dumps(MockServerManager.mock_endpoints)}

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_PATCH(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def handle_request(self):
        path = self.path.split("?")[0]
        method = self.command
        
        key = f"{{method}} {{path}}"
        
        if key in mock_endpoints:
            endpoint = mock_endpoints[key]
            self.send_response(endpoint.get("status_code", 200))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(endpoint.get("response", {{}})).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({{"error": "Not found"}}).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging

server = HTTPServer(("127.0.0.1", {port}), MockHandler)
print("Mock server started on port {port}")
server.serve_forever()
'''
            
            # Create temporary mock server file
            mock_file = os.path.join(os.path.dirname(__file__), "_mock_server.py")
            with open(mock_file, "w") as f:
                f.write(mock_app_code)
            
            # Start server as subprocess
            MockServerManager.mock_process = subprocess.Popen(
                ["python", mock_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except Exception as e:
            print(f"Error starting mock server: {e}")
            return False
    
    @staticmethod
    def stop_mock_server() -> bool:
        """Stop mock HTTP server."""
        try:
            if MockServerManager.mock_process:
                os.kill(MockServerManager.mock_process.pid, signal.SIGTERM)
                MockServerManager.mock_process = None
            return True
        except Exception as e:
            print(f"Error stopping mock server: {e}")
            return False
    
    @staticmethod
    def add_endpoint(method: str, path: str, status_code: int = 200, 
                     response: Dict[str, Any] = None) -> None:
        """Add mock endpoint."""
        key = f"{method.upper()} {path}"
        MockServerManager.mock_endpoints[key] = {
            "status_code": status_code,
            "response": response or {"message": "OK"}
        }
    
    @staticmethod
    def remove_endpoint(method: str, path: str) -> None:
        """Remove mock endpoint."""
        key = f"{method.upper()} {path}"
        if key in MockServerManager.mock_endpoints:
            del MockServerManager.mock_endpoints[key]
    
    @staticmethod
    def get_endpoints() -> Dict[str, Dict[str, Any]]:
        """Get all mock endpoints."""
        return MockServerManager.mock_endpoints


class GraphQLClient:
    """Handle GraphQL queries and schema introspection."""
    
    cached_schemas = {}
    
    @staticmethod
    def execute_query(endpoint: str, query: str, variables: Dict[str, Any] = None,
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute a GraphQL query."""
        try:
            payload = {
                "query": query,
                "variables": variables or {}
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers or {"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.json()
        except Exception as e:
            return {"errors": [{"message": str(e)}]}
    
    @staticmethod
    def introspect_schema(endpoint: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Introspect GraphQL schema."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    kind
                    name
                    description
                    fields {
                        name
                        type { kind name }
                    }
                }
                queryType { name }
                mutationType { name }
            }
        }
        """
        
        result = GraphQLClient.execute_query(endpoint, introspection_query, headers=headers)
        
        if endpoint not in GraphQLClient.cached_schemas:
            GraphQLClient.cached_schemas[endpoint] = result
        
        return result
    
    @staticmethod
    def build_query_from_schema(query_type: str, fields: List[str]) -> str:
        """Build a GraphQL query from schema information."""
        fields_str = "\n    ".join(fields)
        
        if query_type.lower() in ["mutation"]:
            return f"""
mutation {{
    {fields_str}
}}
            """
        else:
            return f"""
query {{
    {fields_str}
}}
            """
    
    @staticmethod
    def validate_query_syntax(query: str) -> Tuple[bool, Optional[str]]:
        """Validate GraphQL query syntax."""
        # Basic validation - check for balanced braces
        try:
            open_braces = query.count("{")
            close_braces = query.count("}")
            
            if open_braces != close_braces:
                return False, "Unbalanced braces in query"
            
            # Check for required keywords
            if not any(kw in query.lower() for kw in ["query", "mutation", "subscription"]):
                return False, "Query must include query, mutation, or subscription keyword"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def format_query(query: str) -> str:
        """Format GraphQL query for better readability."""
        lines = []
        indent_level = 0
        
        for line in query.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            if "}" in line:
                indent_level = max(0, indent_level - 1)
            
            lines.append("  " * indent_level + line)
            
            if "{" in line:
                indent_level += 1
        
        return "\n".join(lines)
