"""FastAPI backend for ApiClient."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add parent directory to path to import apiclient
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apiclient.client import APIClient
from apiclient.config import Config, RequestConfig

app = FastAPI(
    title="ApiClient API",
    description="Backend for ApiClient - HTTP API Testing Tool",
    version="1.0.0",
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
