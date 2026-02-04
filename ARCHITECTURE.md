# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USERS                                    │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
             ▼                                ▼
     ┌──────────────────┐          ┌──────────────────┐
     │  Command Line    │          │   Web Browser    │
     │   (Terminal)     │          │      UI          │
     └────────┬─────────┘          └────────┬─────────┘
              │                            │
              │  (Python CLI)             │  (React + Vite)
              │                            │
              └────────────┬───────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  FastAPI Server  │
                  │  localhost:8000  │
                  └────────┬─────────┘
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
          ┌────────┐  ┌────────┐  ┌────────┐
          │ HTTP  │  │ Config │  │Client │
          │Client │  │Manager │  │Logic  │
          └────────┘  └────────┘  └────────┘
                │
                │  (HTTPS)
                ▼
        ┌────────────────────────┐
        │  External APIs         │
        │ (jsonplaceholder,      │
        │  github, etc.)         │
        └────────────────────────┘
```

## Component Interaction

### CLI Flow
```
User Command
    ↓
Typer CLI Parser (cli.py)
    ↓
APIClient (client.py)
    ↓
HTTP Request to external API
    ↓
Response Parsing
    ↓
Formatted Output (formatter.py)
    ↓
Rich Terminal Display
```

### Web Interface Flow
```
User Action (Browser)
    ↓
React Component (RequestBuilder)
    ↓
Axios HTTP Request
    ↓
FastAPI Backend Server
    ↓
APIClient (client.py)
    ↓
Config Manager (config.py)
    ↓
HTTP Request to external API
    ↓
Response Back to FastAPI
    ↓
JSON Response to Frontend
    ↓
React State Update
    ↓
ResponseViewer Component Display
```

## Data Flow

### Making a Request

```
Frontend Form
    ↓
{method, url, headers, body, params}
    ↓
POST /api/request
    ↓
FastAPI validates input
    ↓
APIClient.make_request()
    ↓
requests.request() to external API
    ↓
Response returned with:
  - status_code
  - headers (dict)
  - body (JSON or text)
  - success (bool)
  - error (if failed)
    ↓
Response displayed in UI
```

### Saving a Request

```
Frontend Save Button
    ↓
User enters: name
    ↓
POST /api/save
{name, method, url, headers, body, params}
    ↓
Config.save_request()
    ↓
JSON written to ~/.apiclient/requests.json
    ↓
Success message displayed
```

## File Storage Structure

```
~/.apiclient/
├── requests.json     # Saved API requests
│   └── Example:
│       {
│         "my-github": {
│           "method": "GET",
│           "url": "https://api.github.com/users/octocat",
│           "headers": {"Authorization": "Bearer ..."},
│           "body": null,
│           "params": {}
│         }
│       }
│
└── history.json      # Request history (last 50)
    └── Example:
        [
          {"method": "GET", "url": "https://api.github.com/users/octocat"},
          {"method": "POST", "url": "https://jsonplaceholder.typicode.com/posts"}
        ]
```

## API Endpoints

```
FastAPI Routes:

├── GET /health
│   └── Returns: {status: "ok", message: "ApiClient backend is running"}
│
├── POST /request
│   ├── Input: {method, url, headers?, body?, params?}
│   └── Output: {status_code, headers, body, success, error?}
│
├── POST /save
│   ├── Input: {name, method, url, headers?, body?, params?}
│   └── Output: {message: "Request saved"}
│
├── GET /requests
│   └── Output: {requests: [list of saved requests]}
│
├── GET /requests/{name}
│   └── Output: {name, method, url, headers, body, params}
│
├── DELETE /requests/{name}
│   └── Output: {message: "Request deleted"}
│
├── GET /history
│   └── Output: {history: [{method, url}, ...]}
│
└── GET /docs (Auto-generated Swagger UI)
    └── Interactive API documentation
```

## Technology Stack

### Backend
```
FastAPI 0.104.1      - Web framework
Uvicorn 0.24.0       - ASGI server
Python 3.8+          - Runtime
Pydantic 2.5.0       - Data validation
Requests 2.31.0      - HTTP client
Typer 0.9.0          - CLI framework
Rich 13.7.0          - Terminal formatting
```

### Frontend
```
React 18.2.0         - UI library
Vite 5.0.2           - Build tool
Axios 1.6.2          - HTTP client
CSS3                 - Styling
```

## Deployment Architecture

### Development Environment
```
localhost:5173 (React Dev Server)
       ↓
localhost:8000 (FastAPI)
       ↓
External APIs
```

### Production Environment
```
Vercel Edge Network (Frontend)
       ↓
Render.com / Railway (Backend API)
       ↓
External APIs
```

## Scalability Considerations

### Current Design
- Single FastAPI instance
- JSON file storage
- Direct HTTP requests

### Future Enhancements
- Database (PostgreSQL) for storing requests
- Caching layer (Redis)
- Load balancing for multiple backend instances
- Request queuing for async processing
- User authentication/authorization
- Rate limiting and throttling
- WebSocket support for real-time updates

## Security Considerations

### Current Implementation
- ✅ CORS enabled (frontend to backend)
- ✅ Input validation (Pydantic)
- ✅ Error handling (no data leaks)
- ✅ Timeout protection (30s default)
- ⚠️ No authentication (local development)
- ⚠️ No rate limiting (local development)

### Production Recommendations
- Add JWT authentication
- Implement rate limiting
- Use HTTPS/SSL certificates
- Add request logging and monitoring
- Implement API key management
- Add user role-based access control
- Sanitize sensitive data in logs

## Performance Metrics

### Expected Performance
- **Request latency**: 100-500ms (depends on external API)
- **Page load time**: <1s (frontend)
- **API response time**: 50-100ms (backend)
- **Storage size**: ~10KB per saved request

### Optimization Opportunities
- Implement request caching
- Add response compression
- Use CDN for static assets
- Implement request batching
- Add GraphQL for flexible queries
