"""
FastAPI backend for ApiClient - Phase 2 & 3 Features
Provides REST endpoints for request chains, templates, auth, mocks, and GraphQL
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import subprocess
import threading
from datetime import datetime
import requests
import time
import os

from apiclient.config import (
    Config, RequestConfig, RequestChain, RequestTemplate, PerformanceMetric,
    AuthenticationConfig, MockEndpoint, GraphQLQuery
)
from apiclient.client import APIClient

app = FastAPI(title="ApiClient API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global config and HTTP client
config = Config()
http_client = APIClient()

# Global mock server process
mock_server_process = None


# ==================== MODELS ====================
class RequestExecutionResult(BaseModel):
    """Result of executing a request"""
    status_code: int
    response: Dict[str, Any]
    time_taken: float
    size: int


class ChainExecutionResult(BaseModel):
    """Result of executing a chain"""
    chain_name: str
    total_time: float
    requests_executed: int
    results: List[RequestExecutionResult]
    variables: Dict[str, Any]


class ImportData(BaseModel):
    """Data for importing requests"""
    format: str  # "postman" | "insomnia" | "openapi"
    data: Dict[str, Any]


# ==================== SAVED REQUESTS ====================
@app.get("/api/requests")
def list_requests():
    """List all saved requests"""
    requests_dict = config.load_requests()
    return {
        "requests": [
            {
                "name": name,
                "method": req.method,
                "url": req.url,
            }
            for name, req in requests_dict.items()
        ],
        "count": len(requests_dict)
    }


@app.get("/api/requests/{name}")
def get_request(name: str):
    """Get a specific saved request"""
    requests_dict = config.load_requests()
    if name not in requests_dict:
        raise HTTPException(status_code=404, detail="Request not found")
    return requests_dict[name].dict()


@app.post("/api/requests")
def create_request(req: RequestConfig):
    """Create or update a saved request"""
    config.save_request(req)
    return {"status": "success", "name": req.name}


@app.delete("/api/requests/{name}")
def delete_request(name: str):
    """Delete a saved request"""
    if config.delete_request(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Request not found")


@app.post("/api/requests/{name}/execute")
def execute_request(name: str):
    """Execute a specific request"""
    requests_dict = config.load_requests()
    if name not in requests_dict:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req = requests_dict[name]
    
    try:
        start = time.time()
        if req.method == "GET":
            resp = requests.get(req.url, headers=dict(req.headers or {}), timeout=30)
        elif req.method == "POST":
            resp = requests.post(req.url, json=req.body, headers=dict(req.headers or {}), timeout=30)
        elif req.method == "PUT":
            resp = requests.put(req.url, json=req.body, headers=dict(req.headers or {}), timeout=30)
        elif req.method == "PATCH":
            resp = requests.patch(req.url, json=req.body, headers=dict(req.headers or {}), timeout=30)
        elif req.method == "DELETE":
            resp = requests.delete(req.url, headers=dict(req.headers or {}), timeout=30)
        else:
            resp = requests.head(req.url, headers=dict(req.headers or {}), timeout=30)
        
        elapsed = time.time() - start
        
        try:
            response_data = resp.json()
        except:
            response_data = {"text": resp.text[:500] if resp.text else ""}
        
        # Save metric with all required fields
        try:
            metric = PerformanceMetric(
                request_name=name,
                status_code=resp.status_code,
                response_time=elapsed,
                timestamp=datetime.now().isoformat(),
                request_size=len(req.url) + len(str(req.body or "")),
                response_size=len(resp.content)
            )
            config.save_metric(metric)
        except Exception as metric_error:
            # Don't fail the request if metric saving fails
            pass
        
        return {
            "status_code": resp.status_code,
            "response": response_data,
            "time_taken": elapsed,
            "size": len(resp.content)
        }
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Connection error")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== REQUEST HISTORY ====================
@app.get("/api/history")
def get_history():
    """Get request history"""
    history = config.load_history()
    return {
        "history": history[-50:],  # Last 50
        "count": len(history)
    }


# ==================== REQUEST CHAINING ====================
@app.get("/api/chains")
def list_chains():
    """List all request chains"""
    chains = config.load_chains()
    return {
        "chains": [
            {
                "name": name,
                "requests": len(chain.requests),
            }
            for name, chain in chains.items()
        ],
        "count": len(chains)
    }


@app.get("/api/chains/{name}")
def get_chain(name: str):
    """Get a specific chain"""
    chains = config.load_chains()
    if name not in chains:
        raise HTTPException(status_code=404, detail="Chain not found")
    return chains[name].dict()


@app.post("/api/chains")
def create_chain(chain: RequestChain):
    """Create or update a request chain"""
    config.save_chain(chain)
    return {"status": "success", "name": chain.name}


@app.delete("/api/chains/{name}")
def delete_chain(name: str):
    """Delete a request chain"""
    if config.delete_chain(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Chain not found")


@app.post("/api/chains/{name}/execute")
def execute_chain(name: str) -> ChainExecutionResult:
    """Execute a request chain sequentially"""
    chains = config.load_chains()
    if name not in chains:
        raise HTTPException(status_code=404, detail="Chain not found")
    
    chain = chains[name]
    results = []
    variables = {}
    total_time = 0
    
    for request_name in chain.requests:
        requests_dict = config.load_requests()
        if request_name not in requests_dict:
            continue
        
        request = requests_dict[request_name]
        
        # Replace variables in URL and body
        url = request.url
        for var_name, var_value in variables.items():
            url = url.replace(f"{{{var_name}}}", str(var_value))
        
        headers = dict(request.headers or {})
        body = request.body
        if body:
            body_str = json.dumps(body) if isinstance(body, dict) else str(body)
            for var_name, var_value in variables.items():
                body_str = body_str.replace(f"{{{var_name}}}", str(var_value))
            body = json.loads(body_str)
        
        # Execute request
        start = time.time()
        try:
            if request.method == "GET":
                resp = requests.get(url, headers=headers)
            elif request.method == "POST":
                resp = requests.post(url, json=body, headers=headers)
            elif request.method == "PUT":
                resp = requests.put(url, json=body, headers=headers)
            elif request.method == "PATCH":
                resp = requests.patch(url, json=body, headers=headers)
            elif request.method == "DELETE":
                resp = requests.delete(url, headers=headers)
            else:
                resp = requests.head(url, headers=headers)
            
            elapsed = time.time() - start
            total_time += elapsed
            
            try:
                response_data = resp.json()
            except:
                response_data = {"text": resp.text}
            
            results.append(RequestExecutionResult(
                status_code=resp.status_code,
                response=response_data,
                time_taken=elapsed,
                size=len(resp.content)
            ))
            
            # Extract variables
            if chain.extract_vars:
                for var_name, var_path in chain.extract_vars.items():
                    try:
                        value = response_data
                        for key in var_path.split("."):
                            value = value[key]
                        variables[var_name] = value
                    except:
                        pass
        except Exception as e:
            results.append(RequestExecutionResult(
                status_code=0,
                response={"error": str(e)},
                time_taken=0,
                size=0
            ))
    
    return ChainExecutionResult(
        chain_name=name,
        total_time=total_time,
        requests_executed=len(results),
        results=results,
        variables=variables
    )


# ==================== REQUEST TEMPLATES ====================
@app.get("/api/templates")
def list_templates():
    """List all request templates"""
    templates = config.load_templates()
    return {
        "templates": [
            {
                "name": name,
                "category": template.category,
                "method": template.method,
            }
            for name, template in templates.items()
        ],
        "count": len(templates)
    }


@app.get("/api/templates/{name}")
def get_template(name: str):
    """Get a specific template"""
    templates = config.load_templates()
    if name not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    return templates[name].dict()


@app.post("/api/templates")
def create_template(template: RequestTemplate):
    """Create or update a template"""
    config.save_template(template)
    return {"status": "success", "name": template.name}


@app.delete("/api/templates/{name}")
def delete_template(name: str):
    """Delete a template"""
    if config.delete_template(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Template not found")


@app.post("/api/templates/{name}/apply")
def apply_template(name: str, overrides: Dict[str, Any]):
    """Apply a template with overrides"""
    templates = config.load_templates()
    if name not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = templates[name]
    request = RequestConfig(
        name=f"{name}_{datetime.now().timestamp()}",
        method=overrides.get("method", template.method),
        url=overrides.get("url", template.base_url),
        headers=overrides.get("headers", template.headers),
        body=overrides.get("body", template.body),
    )
    config.save_request(request)
    return {"status": "success", "request_name": request.name}


# ==================== PERFORMANCE METRICS ====================
@app.get("/api/metrics")
def get_metrics(limit: int = 100):
    """Get performance metrics"""
    metrics = config.load_metrics()
    return {
        "metrics": [m.dict() for m in metrics[-limit:]],
        "count": len(metrics),
        "average_response_time": sum(m.response_time for m in metrics) / len(metrics) if metrics else 0,
    }


@app.post("/api/metrics")
def record_metric(metric: PerformanceMetric):
    """Record a performance metric"""
    config.save_metric(metric)
    return {"status": "success"}


@app.get("/api/metrics/stats")
def get_metrics_stats(endpoint: Optional[str] = None):
    """Get performance statistics"""
    metrics = config.load_metrics()
    
    if endpoint:
        metrics = [m for m in metrics if m.endpoint == endpoint]
    
    if not metrics:
        return {"error": "No metrics found"}
    
    times = [m.response_time for m in metrics]
    return {
        "endpoint": endpoint or "all",
        "count": len(metrics),
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "total_requests": len(metrics),
        "success_rate": len([m for m in metrics if m.status_code < 400]) / len(metrics) * 100,
    }


# ==================== IMPORT/EXPORT ====================
@app.post("/api/import")
def import_requests(import_data: ImportData):
    """Import requests from various formats"""
    count = 0
    
    if import_data.format == "postman":
        # Parse Postman collection
        for item in import_data.data.get("item", []):
            name = item.get("name")
            req = item.get("request", {})
            method = req.get("method", "GET")
            url = req.get("url", {})
            if isinstance(url, dict):
                url = url.get("raw", "")
            
            headers = {h["key"]: h["value"] for h in req.get("header", [])}
            body = req.get("body", {}).get("raw")
            
            saved = RequestConfig(name=name, method=method, url=url, headers=headers, body=body)
            config.save_request(saved)
            count += 1
    
    elif import_data.format == "insomnia":
        # Parse Insomnia export
        for resource in import_data.data.get("resources", []):
            if resource.get("_type") == "request":
                saved = RequestConfig(
                    name=resource.get("name"),
                    method=resource.get("method", "GET"),
                    url=resource.get("url", ""),
                    headers=resource.get("headers", {}),
                    body=resource.get("body", {}).get("text"),
                )
                config.save_request(saved)
                count += 1
    
    return {"status": "success", "imported": count}


@app.get("/api/export")
def export_requests(format: str = "json"):
    """Export all requests"""
    requests_dict = config.load_requests()
    
    if format == "postman":
        collection = {
            "info": {"name": "ApiClient Export", "version": "2.1.0"},
            "item": [
                {
                    "name": name,
                    "request": {
                        "method": req.method,
                        "url": {"raw": req.url},
                        "header": [{"key": k, "value": v} for k, v in (req.headers or {}).items()],
                        "body": {"raw": req.body} if req.body else {},
                    }
                }
                for name, req in requests_dict.items()
            ]
        }
        return collection
    
    return {
        "format": "json",
        "requests": {name: req.dict() for name, req in requests_dict.items()}
    }


# ==================== AUTHENTICATION ====================
@app.get("/api/auth")
def list_auth_configs():
    """List authentication configurations"""
    configs = config.load_auth_configs()
    return {
        "configs": [
            {
                "name": name,
                "type": auth.type,
            }
            for name, auth in configs.items()
        ],
        "count": len(configs)
    }


@app.get("/api/auth/{name}")
def get_auth_config(name: str):
    """Get authentication configuration"""
    configs = config.load_auth_configs()
    if name not in configs:
        raise HTTPException(status_code=404, detail="Auth config not found")
    return configs[name].dict()


@app.post("/api/auth")
def create_auth_config(auth: AuthenticationConfig):
    """Create or update authentication configuration"""
    config.save_auth_config(auth)
    return {"status": "success", "name": auth.name}


@app.delete("/api/auth/{name}")
def delete_auth_config(name: str):
    """Delete authentication configuration"""
    if config.delete_auth_config(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Auth config not found")


@app.post("/api/auth/{name}/oauth2/token")
def get_oauth2_token(name: str):
    """Get OAuth2 token"""
    configs = config.load_auth_configs()
    if name not in configs:
        raise HTTPException(status_code=404, detail="Auth config not found")
    
    auth = configs[name]
    if auth.auth_type != "oauth2":
        raise HTTPException(status_code=400, detail="Not an OAuth2 config")
    
    try:
        response = requests.post(
            auth.oauth2_token_url,
            data={
                "client_id": auth.oauth2_client_id,
                "client_secret": auth.oauth2_client_secret,
                "grant_type": "client_credentials",
            }
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== MOCK SERVER ====================
@app.get("/api/mocks")
def list_mock_endpoints():
    """List mock endpoints"""
    endpoints = config.load_mock_endpoints()
    return {
        "endpoints": [
            {
                "name": name,
                "path": endpoint.path,
                "method": endpoint.method,
            }
            for name, endpoint in endpoints.items()
        ],
        "count": len(endpoints)
    }


@app.post("/api/mocks")
def create_mock_endpoint(endpoint: MockEndpoint):
    """Create mock endpoint"""
    config.save_mock_endpoint(endpoint)
    return {"status": "success", "name": endpoint.name}


@app.delete("/api/mocks/{name}")
def delete_mock_endpoint(name: str):
    """Delete mock endpoint"""
    if config.delete_mock_endpoint(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Mock not found")


@app.post("/api/mocks/server/start")
def start_mock_server(port: int = 8888):
    """Start mock server"""
    global mock_server_process
    
    if mock_server_process and mock_server_process.poll() is None:
        return {"status": "already_running", "port": port}
    
    # TODO: Implement mock server startup
    return {"status": "started", "port": port}


@app.post("/api/mocks/server/stop")
def stop_mock_server():
    """Stop mock server"""
    global mock_server_process
    
    if mock_server_process and mock_server_process.poll() is None:
        mock_server_process.terminate()
        return {"status": "stopped"}
    
    return {"status": "not_running"}


# ==================== GRAPHQL ====================
@app.get("/api/graphql")
def list_graphql_queries():
    """List GraphQL queries"""
    queries = config.load_graphql_queries()
    return {
        "queries": [
            {
                "name": name,
                "endpoint": query.endpoint,
            }
            for name, query in queries.items()
        ],
        "count": len(queries)
    }


@app.get("/api/graphql/{name}")
def get_graphql_query(name: str):
    """Get GraphQL query"""
    queries = config.load_graphql_queries()
    if name not in queries:
        raise HTTPException(status_code=404, detail="Query not found")
    return queries[name].dict()


@app.post("/api/graphql")
def create_graphql_query(query: GraphQLQuery):
    """Create GraphQL query"""
    config.save_graphql_query(query)
    return {"status": "success", "name": query.name}


@app.delete("/api/graphql/{name}")
def delete_graphql_query(name: str):
    """Delete GraphQL query"""
    if config.delete_graphql_query(name):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Query not found")


@app.post("/api/graphql/{name}/execute")
def execute_graphql_query(name: str):
    """Execute GraphQL query"""
    queries = config.load_graphql_queries()
    if name not in queries:
        raise HTTPException(status_code=404, detail="Query not found")
    
    query = queries[name]
    
    try:
        response = requests.post(
            query.endpoint,
            json={"query": query.query_text, "variables": query.variables},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/graphql/{name}/introspect")
def introspect_graphql_schema(name: str):
    """Introspect GraphQL schema"""
    queries = config.load_graphql_queries()
    if name not in queries:
        raise HTTPException(status_code=404, detail="Query not found")
    
    query = queries[name]
    
    introspection_query = """
    query IntrospectionQuery {
      __schema {
        types {
          name
          kind
          description
          fields {
            name
            type { name kind }
          }
        }
      }
    }
    """
    
    try:
        response = requests.post(
            query.endpoint,
            json={"query": introspection_query},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== HEALTH ====================
@app.get("/api/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}


# ==================== STATIC FILES & ROOT ====================
@app.get("/")
def root():
    """Serve the dashboard HTML"""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "API Client Dashboard - Open /docs for API documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
