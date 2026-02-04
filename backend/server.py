"""FastAPI backend for ApiClient."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
import time

# Add parent directory to path to import apiclient
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apiclient.client import APIClient
from apiclient.config import Config, RequestConfig, Environment, Collection, Assertion
from apiclient.phase1 import VariableSubstitution, AssertionValidator

app = FastAPI(
    title="ApiClient API",
    description="Backend for ApiClient - HTTP API Testing Tool",
    version="2.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize client and config
client = APIClient()
config = Config()


class RequestModel(BaseModel):
    """Request model for API calls."""

    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    params: Optional[Dict[str, str]] = None
    environment: Optional[str] = None  # Environment name for variable substitution
    assertions: List[Dict[str, Any]] = []  # Assertions to validate


class EnvironmentModel(BaseModel):
    """Model for creating/updating environments."""
    name: str
    variables: Dict[str, str]


class CollectionModel(BaseModel):
    """Model for creating collections."""
    name: str
    description: Optional[str] = None


class AssertionModel(BaseModel):
    """Model for creating assertions."""
    field: str
    operator: str
    expected: Optional[Any] = None


class SavedRequestModel(BaseModel):
    """Model for saving requests."""
    name: str
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    params: Optional[Dict[str, str]] = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "ApiClient backend is running"}


@app.post("/request")
async def make_request(request: RequestModel) -> Dict[str, Any]:
    """Make an HTTP request."""
    try:
        response = client.make_request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            body=request.body,
            params=request.params,
        )
        
        # Add to history
        config.add_to_history(request.method, request.url)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save")
async def save_request(request: SavedRequestModel) -> Dict[str, str]:
    """Save a request for later use."""
    try:
        request_config = RequestConfig(
            name=request.name,
            method=request.method,
            url=request.url,
            headers=request.headers or {},
            body=request.body,
            params=request.params or {},
        )
        config.save_request(request_config)
        return {"message": f"Request '{request.name}' saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/requests")
async def list_requests() -> Dict[str, Any]:
    """List all saved requests."""
    try:
        requests = config.load_requests()
        return {
            "requests": [
                {
                    "name": name,
                    "method": req.method,
                    "url": req.url,
                    "headers": req.headers,
                    "body": req.body,
                    "params": req.params,
                }
                for name, req in requests.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/requests/{name}")
async def get_request(name: str) -> Dict[str, Any]:
    """Get a specific saved request."""
    try:
        request = config.get_request(name)
        if not request:
            raise HTTPException(status_code=404, detail=f"Request '{name}' not found")
        
        return {
            "name": request.name,
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
            "body": request.body,
            "params": request.params,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/requests/{name}")
async def delete_request(name: str) -> Dict[str, str]:
    """Delete a saved request."""
    try:
        if config.delete_request(name):
            return {"message": f"Request '{name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Request '{name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history() -> Dict[str, Any]:
    """Get request history."""
    try:
        history = config.load_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PHASE 1: ENVIRONMENTS ====================

@app.get("/environments")
async def get_environments() -> Dict[str, Any]:
    """Get all environments."""
    try:
        environments = config.load_environments()
        return {"environments": {name: env.dict() for name, env in environments.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/environments")
async def create_environment(env_data: EnvironmentModel) -> Dict[str, Any]:
    """Create or update an environment."""
    try:
        env = Environment(name=env_data.name, variables=env_data.variables)
        config.save_environment(env)
        return {"message": f"Environment '{env_data.name}' created", "environment": env.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/environments/{name}")
async def delete_environment(name: str) -> Dict[str, str]:
    """Delete an environment."""
    try:
        if config.delete_environment(name):
            return {"message": f"Environment '{name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Environment '{name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PHASE 1: COLLECTIONS ====================

@app.get("/collections")
async def get_collections() -> Dict[str, Any]:
    """Get all collections."""
    try:
        collections = config.load_collections()
        return {"collections": {name: coll.dict() for name, coll in collections.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collections")
async def create_collection(coll_data: CollectionModel) -> Dict[str, Any]:
    """Create a collection."""
    try:
        collection = Collection(name=coll_data.name, description=coll_data.description, requests=[], parent=None)
        config.save_collection(collection)
        return {"message": f"Collection '{coll_data.name}' created", "collection": collection.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/collections/{name}")
async def delete_collection(name: str) -> Dict[str, str]:
    """Delete a collection."""
    try:
        if config.delete_collection(name):
            return {"message": f"Collection '{name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PHASE 1: ENHANCED REQUEST WITH VARIABLES & ASSERTIONS ====================

@app.post("/request/enhanced")
async def make_request_enhanced(request: RequestModel) -> Dict[str, Any]:
    """Make an HTTP request with environment variable substitution and assertions."""
    try:
        # Load environment variables if specified
        variables = {}
        if request.environment:
            env = config.get_environment(request.environment)
            if env:
                variables = env.variables

        # Substitute variables in URL, headers, body, params
        url = VariableSubstitution.substitute(request.url, variables)
        headers = VariableSubstitution.substitute_dict(request.headers or {}, variables)
        body = VariableSubstitution.substitute(request.body, variables)
        params = VariableSubstitution.substitute_dict(request.params or {}, variables)

        # Make the request
        start_time = time.time()
        response = client.make_request(
            method=request.method,
            url=url,
            headers=headers,
            body=body,
            params=params,
        )
        response_time = time.time() - start_time
        response["response_time"] = response_time

        # Validate assertions if provided
        assertions_passed = True
        assertion_errors = []
        if request.assertions:
            assertions_passed, assertion_errors = AssertionValidator.validate(
                response, request.assertions
            )

        # Add assertion results to response
        response["assertions"] = {
            "passed": assertions_passed,
            "errors": assertion_errors,
            "count": len(request.assertions),
        }

        # Add to history
        config.add_to_history(request.method, request.url)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATIC FILES & FRONTEND ====================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

# Check if frontend dist or standalone HTML exists
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
frontend_root = os.path.join(os.path.dirname(__file__), "..", "frontend")
standalone_html = os.path.join(frontend_root, "standalone.html")

# Serve the standalone HTML at root
@app.get("/")
async def serve_root():
    """Serve the React app root or standalone HTML"""
    if os.path.exists(standalone_html):
        return FileResponse(standalone_html)
    
    index_path = os.path.join(frontend_dist, "index.html") if os.path.exists(frontend_dist) else os.path.join(frontend_root, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return HTMLResponse("""
    <html>
        <head>
            <title>ApiClient - API Testing Tool</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; 
                       display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #1e1e1e; color: #fff; }
                .container { text-align: center; }
                h1 { margin-bottom: 20px; }
                p { font-size: 16px; margin: 10px 0; }
                code { background: #333; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 ApiClient - API Testing Tool</h1>
                <p>Backend is running on <code>http://localhost:8000</code></p>
                <p>API Endpoints: <code>/api/*</code></p>
                <p>Health Check: <code>GET /health</code></p>
            </div>
        </body>
    </html>
    """)

# Mount frontend assets if they exist
if os.path.exists(frontend_dist):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files"""
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # For client-side routing, serve index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
