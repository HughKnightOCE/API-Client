# ApiClient - Full Stack HTTP API Testing Tool

A powerful, full-featured HTTP API testing tool available as both a CLI and web interface. Think Postman, but with both terminal and browser options.

## Features

- 🚀 **Make HTTP Requests** - GET, POST, PUT, DELETE, PATCH, HEAD
- 💾 **Save & Load Requests** - Persistent storage for frequently used requests
- 📊 **Formatted Responses** - Beautiful JSON rendering with headers and status codes
- 📋 **Request History** - Automatic tracking of recent API calls
- 🔐 **Headers & Auth** - Full support for custom headers and parameters
- 🌙 **Dark Mode** - Easy on the eyes UI theme
- 🖥️ **Dual Interface** - CLI tool + Modern web application
- 📱 **Responsive Design** - Works on desktop and mobile browsers

## Project Structure

```
apiclient/                 # Python CLI package
├── __main__.py
├── cli.py                # Typer CLI interface
├── client.py             # HTTP request logic
├── config.py             # Request storage
└── formatter.py          # Terminal formatting

backend/                   # FastAPI server
├── server.py             # REST API endpoints
└── requirements.txt

frontend/                  # React web UI
├── src/
│   ├── components/       # React components
│   ├── App.jsx
│   └── main.jsx
├── vite.config.js
├── package.json
└── index.html
```

## Quick Start

### CLI Usage

```bash
# Make a simple GET request
python -m apiclient get https://api.github.com/users/github

# POST with body
python -m apiclient post https://jsonplaceholder.typicode.com/posts \
  --body '{"title": "Hello", "body": "World"}'

# Save a request
python -m apiclient save my-request -m GET -u https://api.example.com/users

# View saved requests
python -m apiclient list

# Execute a saved request
python -m apiclient run my-request
```

### Web Interface

```bash
# Terminal 1: Start backend
cd backend
python server.py

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

## Installation

### CLI Setup

```bash
pip install -r requirements.txt
python -m apiclient --help
```

### Full Stack Setup

```bash
# Backend dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend
npm install
```

## Requirements

### Backend (Python)
- Python 3.8+
- requests 2.31.0
- typer 0.9.0
- rich 13.7.0
- pydantic 2.5.0
- fastapi 0.104.1
- uvicorn 0.24.0

### Frontend (Node.js)
- Node.js 16+
- React 18.2.0
- Axios 1.6.2
- Vite 5.0.2

## Development

```bash
# Run CLI tests
python -m apiclient --help

# Run backend server
python backend/server.py

# Run frontend dev server
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build
```

## API Endpoints

- `GET /health` - Health check
- `POST /request` - Make HTTP request
- `POST /save` - Save a request
- `GET /requests` - List saved requests
- `GET /requests/{name}` - Get specific request
- `DELETE /requests/{name}` - Delete a request
- `GET /history` - Get request history

## Deployment

### Deploy Frontend to Vercel
```bash
cd frontend
npm run build
# Use Vercel CLI or connect GitHub repo
```

### Deploy Backend to Render/Railway
```bash
# Push to GitHub, connect to Render/Railway
# Set build command: pip install -r requirements.txt && pip install -r backend/requirements.txt
# Set start command: python backend/server.py
```

## License

MIT
