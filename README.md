# ApiClient Pro - Enterprise API Testing Platform

A powerful, full-featured HTTP API testing tool with advanced features for API automation, performance monitoring, and collaboration. Available as CLI, web dashboard, and REST API.

## Features

### Core Features
- 🚀 **HTTP Methods** - GET, POST, PUT, DELETE, PATCH, HEAD
- 💾 **Save & Load** - Persistent request storage
- 📊 **Rich Formatting** - Beautiful JSON/XML response rendering
- 📋 **History** - Automatic request tracking
- 🔐 **Security** - Auth configs, API keys, OAuth2, JWT support
- 🖥️ **Dual Interface** - CLI + Web Dashboard
- 📱 **Responsive** - Works on desktop, tablet, mobile

### Phase 2 - Automation & Analytics
- ⛓️ **Request Chaining** - Execute requests sequentially with variable passing
- 📝 **Templates** - Reusable request templates for common patterns
- 📤 **Import/Export** - Postman, Insomnia, OpenAPI format support
- 📈 **Performance Monitoring** - Track response times, success rates, analytics

### Phase 3 - Advanced Features  
- 🔑 **Authentication** - API Key, Bearer, OAuth2, JWT, Basic Auth
- 🎭 **Mock Server** - Local mock API server for testing
- 🔷 **GraphQL** - Query builder, introspection, variable support

## Project Structure

```
api-testing/
├── apiclient/              # Python CLI package
│   ├── __main__.py
│   ├── cli.py             # Typer CLI with Phase 2&3 commands
│   ├── client.py          # HTTP client
│   ├── config.py          # Storage & models
│   └── formatter.py       # Rich formatting
├── app.py                 # FastAPI backend with all endpoints
├── index.html             # Web dashboard
├── requirements.txt       # Python dependencies
└── FEATURES.md           # Detailed feature documentation
```

## Quick Start

### CLI Usage

```bash
# Make HTTP requests
python -m apiclient get https://api.github.com/users/github
python -m apiclient post https://jsonplaceholder.typicode.com/posts --body '{"title": "Test"}'

# Request chaining
python -m apiclient create-chain workflow '["request1", "request2"]'
python -m apiclient execute-chain workflow

# Request templates
python -m apiclient create-template rest-api "REST" GET "https://api.example.com/v1/{resource}"

# Performance monitoring
python -m apiclient show-metrics --limit 50
python -m apiclient metrics-stats

# Authentication
python -m apiclient create-auth-apikey mykey "sk_live_abc123"

# GraphQL
python -m apiclient create-graphql users "https://api.example.com/graphql" '{ users { id name } }'
python -m apiclient execute-graphql users

# Import/Export
python -m apiclient export --format postman > collection.json
python -m apiclient import-requests collection.json --format postman
```

### Web Dashboard

```bash
# Start FastAPI backend
python app.py

# Open dashboard in browser
http://localhost:8000/
```

## Installation

```bash
# Install Python dependencies
pip install requests typer rich pydantic fastapi uvicorn

# Run CLI
python -m apiclient --help

# Run backend
python app.py

# Open dashboard
http://localhost:8000
```

## Architecture

### Request Storage
All data stored in `~/.apiclient/`:
- `requests.json` - Saved HTTP requests
- `chains.json` - Request chains
- `templates.json` - Request templates
- `metrics.json` - Performance data
- `auth.json` - Auth configurations
- `mocks.json` - Mock endpoints
- `graphql.json` - GraphQL queries

### API Endpoints

**Requests:**
- `GET /api/requests` - List all
- `POST /api/requests` - Create
- `GET /api/requests/{name}` - Get specific
- `DELETE /api/requests/{name}` - Delete

**Chains (Phase 2):**
- `GET /api/chains` - List
- `POST /api/chains` - Create
- `POST /api/chains/{name}/execute` - Execute

**Templates (Phase 2):**
- `GET /api/templates` - List
- `POST /api/templates` - Create
- `POST /api/templates/{name}/apply` - Apply

**Performance (Phase 2):**
- `GET /api/metrics` - Get metrics
- `GET /api/metrics/stats` - Get statistics

**Authentication (Phase 3):**
- `GET /api/auth` - List configs
- `POST /api/auth` - Create config
- `POST /api/auth/{name}/oauth2/token` - Get OAuth2 token

**Mocks (Phase 3):**
- `GET /api/mocks` - List endpoints
- `POST /api/mocks` - Create endpoint
- `POST /api/mocks/server/start` - Start server

**GraphQL (Phase 3):**
- `GET /api/graphql` - List queries
- `POST /api/graphql` - Create query
- `POST /api/graphql/{name}/execute` - Execute
- `POST /api/graphql/{name}/introspect` - Introspect schema

**Import/Export (Phase 2):**
- `POST /api/import` - Import requests
- `GET /api/export` - Export all requests

### Deploy Backend to Render/Railway
```bash
# Push to GitHub, connect to Render/Railway
# Set build command: pip install -r requirements.txt && pip install -r backend/requirements.txt
# Set start command: python backend/server.py
```

## License

MIT
