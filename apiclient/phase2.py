"""
Phase 2: Request Chaining, Templates, Import/Export, Performance Monitoring
"""

import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import re


class RequestChainExecutor:
    """Execute chains of requests with variable extraction and substitution."""
    
    @staticmethod
    def extract_value(obj: Dict[str, Any], path: str) -> Any:
        """Extract value from response using dot notation."""
        if not path:
            return None
        
        keys = path.split(".")
        current = obj
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                try:
                    current = current[int(key)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        
        return current
    
    @staticmethod
    def execute_chain(chain_requests: List[Dict[str, Any]], 
                     variables: Dict[str, str], 
                     extract_rules: List[Dict[str, str]]) -> Tuple[bool, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute a chain of requests sequentially.
        
        extract_rules format: [{"response_path": "data.id", "variable_name": "USER_ID"}, ...]
        Returns (success, responses, extracted_variables)
        """
        responses = []
        current_vars = variables.copy()
        
        for i, req in enumerate(chain_requests):
            try:
                # Substitute variables in this request
                url = req.get("url", "")
                for var_name, var_value in current_vars.items():
                    url = url.replace(f"{{{{{var_name}}}}}", str(var_value))
                
                headers = req.get("headers", {})
                for key, value in headers.items():
                    for var_name, var_value in current_vars.items():
                        if isinstance(value, str):
                            value = value.replace(f"{{{{{var_name}}}}}", str(var_value))
                    headers[key] = value
                
                body = req.get("body", "")
                if body:
                    for var_name, var_value in current_vars.items():
                        body = body.replace(f"{{{{{var_name}}}}}", str(var_value))
                
                params = req.get("params", {})
                for key, value in params.items():
                    for var_name, var_value in current_vars.items():
                        if isinstance(value, str):
                            value = value.replace(f"{{{{{var_name}}}}}", str(var_value))
                    params[key] = value
                
                # Make the request
                start_time = time.time()
                response = requests.request(
                    method=req.get("method", "GET"),
                    url=url,
                    headers=headers,
                    json=json.loads(body) if body else None,
                    params=params,
                    timeout=10
                )
                duration = time.time() - start_time
                
                response_data = {
                    "request_index": i,
                    "status_code": response.status_code,
                    "url": url,
                    "duration": duration,
                    "body": response.json() if response.headers.get('content-type', '').find('application/json') >= 0 else response.text,
                    "headers": dict(response.headers)
                }
                responses.append(response_data)
                
                # Extract variables from response for next request
                if i < len(chain_requests) - 1 and extract_rules:
                    for rule in extract_rules:
                        if rule.get("from_request") == i:
                            value = RequestChainExecutor.extract_value(response_data["body"], rule.get("response_path", ""))
                            if value is not None:
                                current_vars[rule.get("variable_name", "")] = str(value)
            
            except Exception as e:
                responses.append({
                    "request_index": i,
                    "error": str(e),
                    "status_code": 0
                })
                return False, responses, current_vars
        
        return True, responses, current_vars


class TemplateManager:
    """Manage request templates for common APIs."""
    
    BUILT_IN_TEMPLATES = {
        "github_api": {
            "name": "GitHub API",
            "category": "REST",
            "description": "GitHub REST API v3 request template",
            "base_url": "https://api.github.com",
            "method": "GET",
            "headers": {
                "Authorization": "Bearer {{GITHUB_TOKEN}}",
                "Accept": "application/vnd.github.v3+json"
            },
            "example_response": {"id": 1, "name": "repository"}
        },
        "stripe_api": {
            "name": "Stripe API",
            "category": "REST",
            "description": "Stripe REST API request template",
            "base_url": "https://api.stripe.com/v1",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer {{STRIPE_API_KEY}}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "example_response": {"object": "charge", "id": "ch_1234"}
        },
        "slack_api": {
            "name": "Slack API",
            "category": "REST",
            "description": "Slack Webhook or API request template",
            "base_url": "https://hooks.slack.com/services",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": '{"text": "Message from {{APP_NAME}}", "channel": "{{CHANNEL}}"}',
            "example_response": {"ok": True}
        },
        "jsonplaceholder": {
            "name": "JSONPlaceholder",
            "category": "REST",
            "description": "JSONPlaceholder test API template",
            "base_url": "https://jsonplaceholder.typicode.com",
            "method": "GET",
            "example_response": {"userId": 1, "id": 1, "title": "test"}
        },
        "openai_api": {
            "name": "OpenAI API",
            "category": "REST",
            "description": "OpenAI Chat Completion API",
            "base_url": "https://api.openai.com/v1",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer {{OPENAI_API_KEY}}",
                "Content-Type": "application/json"
            },
            "body": '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "{{MESSAGE}}"}]}',
            "example_response": {"choices": [{"message": {"content": "response"}}]}
        }
    }
    
    @staticmethod
    def get_built_in_templates() -> Dict[str, Dict[str, Any]]:
        """Return all built-in templates."""
        return TemplateManager.BUILT_IN_TEMPLATES
    
    @staticmethod
    def apply_template(template: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a template with overrides."""
        result = template.copy()
        result.update(overrides)
        return result


class ImportExportManager:
    """Handle importing/exporting requests from various formats."""
    
    @staticmethod
    def parse_postman_collection(collection_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Postman collection format."""
        requests_list = []
        
        def extract_items(items: List[Any], parent_folder: str = ""):
            for item in items:
                if "item" in item:
                    # Folder
                    extract_items(item["item"], parent_folder + "/" + item.get("name", ""))
                elif "request" in item:
                    # Request
                    req = item["request"]
                    url = ""
                    if isinstance(req.get("url"), dict):
                        url = req["url"].get("raw", "")
                    else:
                        url = req.get("url", "")
                    
                    headers = {}
                    if isinstance(req.get("header"), list):
                        headers = {h["key"]: h["value"] for h in req["header"]}
                    
                    body = ""
                    if req.get("body"):
                        body = req["body"].get("raw", "")
                    
                    requests_list.append({
                        "name": item.get("name", "Untitled"),
                        "method": req.get("method", "GET"),
                        "url": url,
                        "headers": headers,
                        "body": body,
                        "folder": parent_folder
                    })
        
        if "item" in collection_json:
            extract_items(collection_json["item"])
        
        return requests_list
    
    @staticmethod
    def parse_openapi_spec(spec_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse OpenAPI/Swagger specification."""
        requests_list = []
        base_path = spec_json.get("basePath", "")
        base_url = ""
        
        servers = spec_json.get("servers", [])
        if servers:
            base_url = servers[0].get("url", "")
        
        paths = spec_json.get("paths", {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() not in ["get", "post", "put", "patch", "delete", "head", "options"]:
                    continue
                
                url = base_url + base_path + path
                
                headers = {}
                parameters = operation.get("parameters", [])
                for param in parameters:
                    if param.get("in") == "header":
                        headers[param.get("name", "")] = "{{VALUE}}"
                
                requests_list.append({
                    "name": operation.get("summary", f"{method.upper()} {path}"),
                    "method": method.upper(),
                    "url": url,
                    "headers": headers,
                    "description": operation.get("description", "")
                })
        
        return requests_list


class PerformanceMonitor:
    """Track and analyze request performance metrics."""
    
    @staticmethod
    def calculate_statistics(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance statistics from metrics."""
        if not metrics:
            return {}
        
        response_times = [m.get("response_time", 0) for m in metrics if m.get("response_time")]
        status_codes = [m.get("status_code", 0) for m in metrics]
        
        if not response_times:
            return {}
        
        response_times.sort()
        
        return {
            "total_requests": len(metrics),
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p50_response_time": response_times[len(response_times) // 2],
            "p95_response_time": response_times[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0],
            "p99_response_time": response_times[int(len(response_times) * 0.99)] if len(response_times) > 1 else response_times[0],
            "successful_requests": sum(1 for sc in status_codes if 200 <= sc < 300),
            "failed_requests": sum(1 for sc in status_codes if sc >= 400),
            "success_rate": sum(1 for sc in status_codes if 200 <= sc < 300) / len(status_codes) * 100 if status_codes else 0
        }
    
    @staticmethod
    def run_load_test(url: str, method: str = "GET", headers: Dict = None, 
                      body: str = "", num_requests: int = 10, 
                      concurrent: bool = False) -> Dict[str, Any]:
        """Run a simple load test."""
        metrics = []
        errors = []
        
        for i in range(num_requests):
            try:
                start = time.time()
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=json.loads(body) if body else None,
                    timeout=10
                )
                duration = time.time() - start
                
                metrics.append({
                    "request_num": i + 1,
                    "status_code": response.status_code,
                    "response_time": duration,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                errors.append({"request_num": i + 1, "error": str(e)})
        
        stats = PerformanceMonitor.calculate_statistics(metrics)
        stats["errors"] = errors
        stats["metrics"] = metrics
        
        return stats
