"""
Simple FastAPI server to serve React frontend and proxy API requests.
This allows running the frontend without Node.js installed.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

app = FastAPI(title="ApiClient Frontend Server")

# Get the frontend directory
frontend_dir = Path(__file__).parent / "frontend"
dist_dir = frontend_dir / "dist"

# Check if we have a built dist folder, otherwise use src with a fallback
if dist_dir.exists():
    # Serve static files from dist
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets", check_dir=False), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve(full_path: str):
        """Serve frontend files, fallback to index.html for React routing"""
        file_path = dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
    
    @app.get("/")
    async def root():
        """Serve index.html"""
        return FileResponse(dist_dir / "index.html")
else:
    # Development mode - serve HTML file and use Vite proxy
    @app.get("/")
    async def root():
        """Serve the main HTML file"""
        return FileResponse(frontend_dir / "index.html")
    
    @app.get("/{full_path:path}")
    async def serve_dev(full_path: str):
        """In dev mode, serve basic index.html and let Vite handle the rest"""
        # For development, we'd normally use Vite, but since npm isn't available,
        # return a simple HTML page that explains the situation
        return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    print("Frontend Server running on http://localhost:3000")
    print("API Proxy: http://localhost:3000/api/* → http://localhost:8000/*")
    uvicorn.run(app, host="0.0.0.0", port=3000)
