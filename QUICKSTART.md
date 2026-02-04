# Quick Start Guide - ApiClient Pro Phase 2 & 3

## Overview

ApiClient Pro now includes Phase 2 and Phase 3 features for advanced HTTP API testing:

- **Phase 2**: Request Chaining, Templates, Import/Export, Performance Monitoring
- **Phase 3**: Authentication Helpers, Mock Server, GraphQL Support

## Installation

```bash
# Navigate to project directory
cd "C:\Users\Hugh\Qsync\Coding projects\API Testing"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Dependencies already installed (FastAPI, Uvicorn, Pydantic, Requests, Rich, Typer)
```

## Start the API Server

```bash
# Method 1: Using Uvicorn (Recommended)
python -m uvicorn app:app --host 127.0.0.1 --port 8000

# Method 2: Direct Python
python app.py
```

The API will be available at: `http://localhost:8000`

## Access the Web Dashboard

Open your browser and go to:
```
http://localhost:8000/
```

The dashboard includes 9 tabs:
1. **Dashboard** - Overview with statistics
2. **Requests** - Manage saved HTTP requests
3. **Chains** - Create and execute request chains
4. **Templates** - Browse and apply request templates
5. **Performance** - View performance metrics and statistics
6. **Auth** - Configure authentication methods
7. **Mocks** - Define mock HTTP endpoints
8. **GraphQL** - Execute and manage GraphQL queries
9. **Import/Export** - Import from Postman/Insomnia, export in multiple formats

## CLI Commands

```bash
# Request Management
python -m apiclient get https://api.example.com/users
python -m apiclient post https://api.example.com/users --body '{"name":"John"}'
python -m apiclient save my-request

# Chains
python -m apiclient create-chain my-chain '["request1", "request2"]'
python -m apiclient execute-chain my-chain
python -m apiclient list-chains

# Templates
python -m apiclient create-template rest-api REST GET https://api.example.com/v1/{resource}
python -m apiclient list-templates

# Performance Monitoring
python -m apiclient show-metrics
python -m apiclient metrics-stats

# Authentication
python -m apiclient create-auth-apikey my-api-key sk_live_123 --header X-API-Key
python -m apiclient list-auth

# GraphQL
python -m apiclient create-graphql my-query https://api.github.com/graphql 'query { viewer { login } }'
python -m apiclient execute-graphql my-query

# Import/Export
python -m apiclient export --format json > requests.json
python -m apiclient import-requests requests.json --format postman
```

## Test the Installation

Run the comprehensive demo:

```bash
python demo_phase2_3.py
```

This will:
- Create test requests and chains
- Create request templates
- Record performance metrics
- Create authentication configs
- Define mock endpoints
- Create GraphQL queries
- Test import/export functionality

## API Endpoints Reference

### Requests
- `GET /api/requests` - List all requests
- `GET /api/requests/{name}` - Get specific request
- `POST /api/requests` - Create request
- `DELETE /api/requests/{name}` - Delete request

### Chains (NEW)
- `GET /api/chains` - List chains
- `POST /api/chains` - Create chain
- `POST /api/chains/{name}/execute` - Execute chain

### Templates (NEW)
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `POST /api/templates/{name}/apply` - Apply template with overrides

### Metrics (NEW)
- `GET /api/metrics` - Get metrics
- `POST /api/metrics` - Record metric
- `GET /api/metrics/stats` - Get statistics

### Authentication (NEW)
- `GET /api/auth` - List auth configs
- `POST /api/auth` - Create auth config
- `POST /api/auth/{name}/oauth2/token` - Get OAuth2 token

### Mock Server (NEW)
- `GET /api/mocks` - List mock endpoints
- `POST /api/mocks` - Create mock endpoint
- `POST /api/mocks/server/start` - Start mock server
- `POST /api/mocks/server/stop` - Stop mock server

### GraphQL (NEW)
- `GET /api/graphql` - List queries
- `POST /api/graphql` - Create query
- `POST /api/graphql/{name}/execute` - Execute query
- `POST /api/graphql/{name}/introspect` - Introspect schema

### System
- `GET /api/health` - Health check
- `GET /api/history` - Request history

## Data Storage

All data is stored locally in: `~/.apiclient/`

```
~/.apiclient/
├── requests.json      # Saved requests
├── chains.json        # Request chains
├── templates.json     # Request templates
├── metrics.json       # Performance metrics (last 1000)
├── auth.json          # Authentication configs
├── mocks.json         # Mock endpoints
├── graphql.json       # GraphQL queries
└── history.json       # Request history
```

## Common Use Cases

### Use Case 1: Test a REST API Workflow

1. Create requests:
   ```bash
   python -m apiclient post https://api.example.com/users --body '{"name":"John"}'
   python -m apiclient get https://api.example.com/users/1
   ```

2. Create a chain:
   ```bash
   python -m apiclient create-chain user-workflow '["post-user", "get-user"]'
   ```

3. Execute the chain:
   ```bash
   python -m apiclient execute-chain user-workflow
   ```

### Use Case 2: Monitor API Performance

1. Execute requests and they'll be tracked automatically
2. View metrics:
   ```bash
   python -m apiclient show-metrics
   ```
3. View statistics:
   ```bash
   python -m apiclient metrics-stats
   ```

### Use Case 3: Use Request Templates

1. Create a template for GitHub API:
   ```bash
   python -m apiclient create-template github REST GET https://api.github.com/{endpoint}
   ```

2. Apply it with different endpoints:
   - Browse templates in dashboard
   - Click "Apply" and override the endpoint
   - Request is created with template settings

### Use Case 4: Authenticate Requests

1. Create an API key authentication:
   ```bash
   python -m apiclient create-auth-apikey my-api sk_live_key --header X-API-Key
   ```

2. Use in requests:
   - Open dashboard
   - Create request with auth headers
   - Select authentication from Auth tab

### Use Case 5: GraphQL Queries

1. Create a GraphQL query:
   ```bash
   python -m apiclient create-graphql github-user https://api.github.com/graphql 'query { viewer { login repositories(first: 10) { edges { node { name } } } } }'
   ```

2. Execute:
   ```bash
   python -m apiclient execute-graphql github-user
   ```

## Troubleshooting

**Q: Server starts but shuts down immediately**
A: Check that no other process is using port 8000. Try different port:
```bash
python -m uvicorn app:app --port 8001
```

**Q: API returns 404**
A: Ensure you're calling the correct endpoint path (includes `/api` prefix)

**Q: Requests not saving**
A: Check that `~/.apiclient/` directory exists and is writable

**Q: Demo script fails**
A: Ensure all dependencies installed: `pip install fastapi uvicorn requests pydantic rich typer httpx`

## Next Steps

1. **Explore the Web Dashboard**: User-friendly interface for all features
2. **Try Request Chaining**: Execute complex workflows
3. **Monitor Performance**: Track API response times
4. **Use Templates**: Speed up repetitive requests
5. **Test GraphQL**: Execute GraphQL queries directly
6. **Set Up Authentication**: Secure your API tests

## Documentation

- [Features Documentation](FEATURES.md) - Detailed feature descriptions
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical architecture
- [Test Results](TEST_RESULTS.md) - Comprehensive test results

## Support

For issues or feature requests, visit:
https://github.com/HughKnightOCE/API-Client

---

**Happy API Testing!** 🚀
