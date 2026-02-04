# Phase 2 & Phase 3 Features Documentation

This document describes all Phase 2 and Phase 3 features implemented in ApiClient Pro.

## Phase 2 Features

### 1. Request Chaining

Execute multiple requests sequentially with variable passing between requests.

**CLI:**
```bash
# Create a chain
apiclient create-chain mychain '["get_user", "update_user", "get_user_again"]'

# Execute a chain
apiclient execute-chain mychain

# List chains
apiclient list-chains

# Delete a chain
apiclient delete-chain mychain
```

**API Endpoints:**
- `GET /api/chains` - List all chains
- `GET /api/chains/{name}` - Get specific chain
- `POST /api/chains` - Create chain
- `DELETE /api/chains/{name}` - Delete chain
- `POST /api/chains/{name}/execute` - Execute chain

**Features:**
- Sequential request execution
- Variable extraction from responses
- Variable substitution in subsequent requests
- Total time tracking
- Individual request timing

### 2. Request Templates

Reusable request templates for common API patterns.

**CLI:**
```bash
# Create a template
apiclient create-template rest-api "REST" GET "https://api.example.com/v1/{resource}"

# List templates
apiclient list-templates

# Delete a template
apiclient delete-template rest-api
```

**API Endpoints:**
- `GET /api/templates` - List templates
- `GET /api/templates/{name}` - Get template
- `POST /api/templates` - Create template
- `DELETE /api/templates/{name}` - Delete template
- `POST /api/templates/{name}/apply` - Apply template

**Features:**
- Pre-built templates for popular APIs
- Template categories (REST, GraphQL, SOAP, etc.)
- Template documentation
- Quick template application with overrides

### 3. Import/Export

Import requests from Postman, Insomnia, or OpenAPI formats. Export your requests.

**CLI:**
```bash
# Export requests
apiclient export --format json > requests.json
apiclient export --format postman > postman.json

# Import requests
apiclient import-requests requests.json --format postman
```

**API Endpoints:**
- `POST /api/import` - Import requests
- `GET /api/export` - Export all requests

**Supported Formats:**
- **Postman Collection**: Import/export Postman collections
- **Insomnia Export**: Import Insomnia exports
- **OpenAPI Spec**: Import OpenAPI/Swagger specs
- **JSON**: Custom JSON format

### 4. Performance Monitoring

Track performance metrics for all requests.

**CLI:**
```bash
# Show metrics
apiclient show-metrics --limit 100

# Show statistics
apiclient metrics-stats --endpoint https://api.example.com/users
```

**API Endpoints:**
- `GET /api/metrics` - Get recent metrics
- `POST /api/metrics` - Record metric
- `GET /api/metrics/stats` - Get statistics

**Metrics Tracked:**
- Response time
- Status code
- Response size
- Endpoint URL
- Timestamp
- Success/error status

**Statistics Available:**
- Average response time
- Min/max response times
- Success rate percentage
- Total request count

## Phase 3 Features

### 1. Authentication Helpers

Support for multiple authentication methods.

**CLI:**
```bash
# Create API key auth
apiclient create-auth-apikey mykey "sk_live_abc123" --header "X-API-Key"

# List auth configs
apiclient list-auth

# Delete auth config
apiclient delete-auth mykey
```

**API Endpoints:**
- `GET /api/auth` - List configs
- `GET /api/auth/{name}` - Get config
- `POST /api/auth` - Create config
- `DELETE /api/auth/{name}` - Delete config
- `POST /api/auth/{name}/oauth2/token` - Get OAuth2 token

**Supported Auth Types:**
- **API Key**: Static API keys in headers
- **Bearer Token**: Bearer token authentication
- **OAuth2**: Client credentials flow
- **JWT**: JSON Web Token with signing
- **Basic Auth**: Username/password encoding

**Features:**
- Store credentials securely
- Multiple auth methods per workspace
- Quick auth injection into requests
- OAuth2 token refresh
- JWT automatic signing

### 2. Mock Server

Run a local mock server to test your client code.

**CLI:**
```bash
# Create mock endpoint
apiclient create-mock-endpoint user-response "/api/users/{id}" GET

# List mocks
apiclient list-mocks

# Delete mock
apiclient delete-mock-endpoint user-response
```

**API Endpoints:**
- `GET /api/mocks` - List endpoints
- `POST /api/mocks` - Create endpoint
- `DELETE /api/mocks/{name}` - Delete endpoint
- `POST /api/mocks/server/start?port=8888` - Start server
- `POST /api/mocks/server/stop` - Stop server

**Features:**
- Create mock endpoints
- Define custom responses
- Support for path parameters
- Query string handling
- HTTP status code control
- Response delay simulation
- Request logging

### 3. GraphQL Support

Execute GraphQL queries and mutations.

**CLI:**
```bash
# Create GraphQL query
apiclient create-graphql users "https://api.example.com/graphql" '{ users { id name } }'

# Execute query
apiclient execute-graphql users

# List queries
apiclient list-graphql

# Delete query
apiclient delete-graphql users
```

**API Endpoints:**
- `GET /api/graphql` - List queries
- `GET /api/graphql/{name}` - Get query
- `POST /api/graphql` - Create query
- `DELETE /api/graphql/{name}` - Delete query
- `POST /api/graphql/{name}/execute` - Execute query
- `POST /api/graphql/{name}/introspect` - Introspect schema

**Features:**
- Store GraphQL queries
- Query variables support
- Schema introspection
- Query validation
- Response formatting
- Query history

## Data Storage

All data is stored in `~/.apiclient/`:

```
~/.apiclient/
├── requests.json      # Saved requests
├── chains.json        # Request chains
├── templates.json     # Request templates
├── metrics.json       # Performance metrics
├── auth.json          # Auth configurations
├── mocks.json         # Mock endpoints
├── graphql.json       # GraphQL queries
└── history.json       # Request history
```

## Running the Backend API

The backend provides REST endpoints for all features:

```bash
# Install dependencies
pip install fastapi uvicorn requests pydantic

# Run the server
python app.py

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

## Web Dashboard

Access the interactive dashboard at `http://localhost:8000`:

- **Dashboard**: Overview of all data
- **Requests**: Manage saved requests
- **Chains**: Create and execute chains
- **Templates**: Browse and apply templates
- **Performance**: View metrics and statistics
- **Auth**: Manage authentication configs
- **Mocks**: Configure mock server
- **GraphQL**: Execute GraphQL queries
- **Import/Export**: Import/export data

## Examples

### Chaining Example

```
1. Create chain with requests: ["get_posts", "like_post", "get_posts_updated"]
2. First request returns list of posts with IDs
3. Extract post ID from response
4. Use post ID in second request
5. Third request shows updated posts
```

### Template Example

```
1. Create template: REST API → GET → https://api.example.com/v1/{resource}
2. Apply template with overrides: resource=users
3. Creates request: GET https://api.example.com/v1/users
```

### Performance Monitoring Example

```
1. Make requests through CLI or API
2. Each response is recorded as metric
3. View dashboard or CLI stats
4. See avg response time, success rate, etc.
```

### Authentication Example

```
1. Create API key: sk_live_abc123
2. Apply to requests
3. All requests include: X-API-Key: sk_live_abc123
```

### Mock Server Example

```
1. Create mock: GET /api/users → {"id": 1, "name": "John"}
2. Start mock server on port 8888
3. Make request to http://localhost:8888/api/users
4. Get mocked response
```

### GraphQL Example

```
1. Create query: { users { id name email } }
2. Execute against https://api.example.com/graphql
3. View formatted response
4. Save for later use
```

## Performance Considerations

- **Chains**: Limited to 100 requests per chain for performance
- **Metrics**: Stores last 1000 metrics to prevent storage issues
- **Mock Server**: Runs on separate port, doesn't interfere with main API
- **GraphQL**: Schema caching for repeated introspection

## Security Notes

- Store sensitive data in auth configs
- Don't commit `~/.apiclient/` directory to version control
- Use environment variables for tokens when possible
- API keys are stored in plain text - use cautiously

## Future Enhancements

- Database backend for metrics
- Team collaboration features
- Advanced request scheduling
- Webhook support
- API documentation generation
- Load testing with benchmarks
- Custom middleware/plugins
