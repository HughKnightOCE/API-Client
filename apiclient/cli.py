"""CLI interface using Typer."""

import typer
from typing import Optional
import json

from apiclient.client import APIClient
from apiclient.config import Config, RequestConfig
from apiclient.formatter import (
    print_response,
    print_request_info,
    print_table,
    print_success,
    print_error,
    print_info,
)

app = typer.Typer(
    help="HTTP API Testing CLI Tool - Make requests, save them, and manage your API workflows.",
    no_args_is_help=True,
)

client = APIClient()
config = Config()


def make_request_helper(
    method: str,
    url: str,
    headers: Optional[str] = None,
    body: Optional[str] = None,
    params: Optional[str] = None,
):
    """Helper function to make and display an HTTP request."""
    parsed_headers = {}
    parsed_params = {}

    if headers:
        try:
            parsed_headers = json.loads(headers)
        except json.JSONDecodeError:
            print_error("Invalid JSON for headers")
            raise typer.Exit(1)

    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError:
            print_error("Invalid JSON for params")
            raise typer.Exit(1)

    print_request_info(method, url, parsed_headers, body)

    response = client.make_request(method, url, parsed_headers, body, parsed_params)
    print_response(response)

    config.add_to_history(method, url)


@app.command()
def get(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(
        None, "--headers", "-H", help="JSON headers (e.g. '{\"Authorization\": \"Bearer token\"}'"
    ),
    params: Optional[str] = typer.Option(
        None, "--params", "-p", help="Query parameters as JSON"
    ),
):
    """Make a GET request."""
    make_request_helper("GET", url, headers, None, params)


@app.command()
def post(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="Request body (JSON or text)"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters as JSON"),
):
    """Make a POST request."""
    make_request_helper("POST", url, headers, body, params)


@app.command()
def put(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="Request body (JSON or text)"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters as JSON"),
):
    """Make a PUT request."""
    make_request_helper("PUT", url, headers, body, params)


@app.command()
def patch(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="Request body (JSON or text)"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters as JSON"),
):
    """Make a PATCH request."""
    make_request_helper("PATCH", url, headers, body, params)


@app.command()
def delete(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters as JSON"),
):
    """Make a DELETE request."""
    make_request_helper("DELETE", url, headers, None, params)


@app.command()
def head(
    url: str = typer.Argument(..., help="URL to request"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters as JSON"),
):
    """Make a HEAD request."""
    make_request_helper("HEAD", url, headers, None, params)


@app.command()
def save(
    name: str = typer.Argument(..., help="Name to save request as"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    url: str = typer.Option(..., "--url", "-u", help="URL"),
    headers: Optional[str] = typer.Option(None, "--headers", "-H", help="JSON headers"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="Request body"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Query parameters"),
):
    """Save a request for later use."""
    parsed_headers = {}
    parsed_params = {}

    if headers:
        try:
            parsed_headers = json.loads(headers)
        except json.JSONDecodeError:
            print_error("Invalid JSON for headers")
            raise typer.Exit(1)

    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError:
            print_error("Invalid JSON for params")
            raise typer.Exit(1)

    request_config = RequestConfig(
        name=name,
        method=method.upper(),
        url=url,
        headers=parsed_headers,
        body=body,
        params=parsed_params,
    )

    config.save_request(request_config)
    print_success(f"Request '{name}' saved successfully")


@app.command()
def list(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full request details"),
):
    """List all saved requests."""
    requests = config.load_requests()

    if not requests:
        print_info("No saved requests yet. Use 'save' command to save requests.")
        return

    if verbose:
        for name, req in requests.items():
            print_info(f"\n{name}")
            print(f"  Method: {req.method}")
            print(f"  URL: {req.url}")
            if req.headers:
                print(f"  Headers: {json.dumps(req.headers)}")
            if req.body:
                print(f"  Body: {req.body}")
            if req.params:
                print(f"  Params: {json.dumps(req.params)}")
    else:
        rows = [[name, req.method, req.url] for name, req in requests.items()]
        print_table("Saved Requests", rows, ["Name", "Method", "URL"])


@app.command()
def show(name: str = typer.Argument(..., help="Name of saved request")):
    """Show details of a saved request."""
    request = config.get_request(name)

    if not request:
        print_error(f"Request '{name}' not found")
        raise typer.Exit(1)

    print_info(f"Request: {name}")
    print(f"  Method: {request.method}")
    print(f"  URL: {request.url}")

    if request.headers:
        print(f"  Headers: {json.dumps(request.headers, indent=4)}")

    if request.params:
        print(f"  Params: {json.dumps(request.params, indent=4)}")

    if request.body:
        print(f"  Body: {request.body}")


@app.command()
def run(name: str = typer.Argument(..., help="Name of saved request")):
    """Execute a saved request."""
    request = config.get_request(name)

    if not request:
        print_error(f"Request '{name}' not found")
        raise typer.Exit(1)

    print_request_info(request.method, request.url, request.headers, request.body)

    response = client.make_request(
        request.method,
        request.url,
        request.headers,
        request.body,
        request.params,
    )

    print_response(response)
    config.add_to_history(request.method, request.url)


@app.command()
def delete_request(name: str = typer.Argument(..., help="Name of request to delete")):
    """Delete a saved request."""
    if config.delete_request(name):
        print_success(f"Request '{name}' deleted")
    else:
        print_error(f"Request '{name}' not found")
        raise typer.Exit(1)


# ==================== CHAINS ====================
@app.command()
def list_chains():
    """List all request chains."""
    chains = config.load_chains()
    if not chains:
        print_info("No chains found")
        return
    
    data = [[name, len(c.requests)] for name, c in chains.items()]
    print_table(["Name", "Requests"], data)


@app.command()
def create_chain(name: str, requests: str):
    """Create a request chain.
    
    Example: apiclient create-chain mychain '["req1", "req2", "req3"]'
    """
    try:
        req_list = json.loads(requests)
        from apiclient.config import RequestChain
        chain = RequestChain(name=name, requests=req_list)
        config.save_chain(chain)
        print_success(f"Chain '{name}' created with {len(req_list)} requests")
    except json.JSONDecodeError:
        print_error("Invalid JSON for requests list")
        raise typer.Exit(1)


@app.command()
def execute_chain(name: str):
    """Execute a request chain."""
    chains = config.load_chains()
    if name not in chains:
        print_error(f"Chain '{name}' not found")
        raise typer.Exit(1)
    
    chain = chains[name]
    variables = {}
    
    for request_name in chain.requests:
        print_info(f"Executing {request_name}...")
        request = config.get_request(request_name)
        
        if not request:
            print_error(f"Request '{request_name}' not found")
            continue
        
        response = client.make_request(
            request.method,
            request.url,
            request.headers,
            request.body,
            request.params,
        )
        
        print_response(response)
        config.add_to_history(request.method, request.url)
    
    print_success("Chain executed successfully")


@app.command()
def delete_chain(name: str):
    """Delete a request chain."""
    if config.delete_chain(name):
        print_success(f"Chain '{name}' deleted")
    else:
        print_error(f"Chain '{name}' not found")
        raise typer.Exit(1)


# ==================== TEMPLATES ====================
@app.command()
def list_templates():
    """List all request templates."""
    templates = config.load_templates()
    if not templates:
        print_info("No templates found")
        return
    
    data = [[name, t.category, t.method] for name, t in templates.items()]
    print_table(["Name", "Category", "Method"], data)


@app.command()
def create_template(name: str, category: str, method: str, url: str):
    """Create a request template."""
    from apiclient.config import RequestTemplate
    template = RequestTemplate(
        name=name,
        category=category,
        method=method,
        url=url,
    )
    config.save_template(template)
    print_success(f"Template '{name}' created")


@app.command()
def delete_template(name: str):
    """Delete a request template."""
    if config.delete_template(name):
        print_success(f"Template '{name}' deleted")
    else:
        print_error(f"Template '{name}' not found")
        raise typer.Exit(1)


# ==================== PERFORMANCE ====================
@app.command()
def show_metrics(limit: int = typer.Option(50, help="Number of metrics to show")):
    """Show performance metrics."""
    metrics = config.load_metrics()
    if not metrics:
        print_info("No metrics found")
        return
    
    metrics = metrics[-limit:]
    data = [
        [m.endpoint, m.status_code, f"{m.response_time:.2f}ms", m.timestamp]
        for m in metrics
    ]
    print_table(["Endpoint", "Status", "Time", "Timestamp"], data)


@app.command()
def metrics_stats(endpoint: Optional[str] = None):
    """Show performance statistics."""
    metrics = config.load_metrics()
    
    if endpoint:
        metrics = [m for m in metrics if m.endpoint == endpoint]
    
    if not metrics:
        print_error("No metrics found")
        return
    
    times = [m.response_time for m in metrics]
    success = len([m for m in metrics if m.status_code < 400])
    
    print_info(f"Endpoint: {endpoint or 'All'}")
    print(f"  Total Requests: {len(metrics)}")
    print(f"  Avg Response Time: {sum(times) / len(times):.2f}ms")
    print(f"  Min Response Time: {min(times):.2f}ms")
    print(f"  Max Response Time: {max(times):.2f}ms")
    print(f"  Success Rate: {success / len(metrics) * 100:.1f}%")


# ==================== IMPORT/EXPORT ====================
@app.command()
def export(format: str = typer.Option("json", help="Export format: json, postman")):
    """Export all requests."""
    requests_dict = config.load_requests()
    
    if format == "postman":
        data = {
            "info": {"name": "ApiClient Export"},
            "item": [
                {
                    "name": name,
                    "request": {
                        "method": req.method,
                        "url": req.url,
                    }
                }
                for name, req in requests_dict.items()
            ]
        }
    else:
        data = {name: req.dict() for name, req in requests_dict.items()}
    
    print(json.dumps(data, indent=2))


@app.command()
def import_requests(file: str, format: str = typer.Option("postman")):
    """Import requests from file."""
    try:
        with open(file, "r") as f:
            data = json.load(f)
        
        if format == "postman":
            for item in data.get("item", []):
                req = item.get("request", {})
                from apiclient.config import SavedRequest
                saved = SavedRequest(
                    name=item.get("name"),
                    method=req.get("method", "GET"),
                    url=req.get("url", ""),
                )
                config.save_request(saved)
        
        print_success(f"Imported {len(data.get('item', []))} requests")
    except FileNotFoundError:
        print_error(f"File '{file}' not found")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        print_error("Invalid JSON file")
        raise typer.Exit(1)


# ==================== AUTHENTICATION ====================
@app.command()
def list_auth():
    """List all authentication configs."""
    configs = config.load_auth_configs()
    if not configs:
        print_info("No auth configs found")
        return
    
    data = [[name, c.auth_type] for name, c in configs.items()]
    print_table(["Name", "Type"], data)


@app.command()
def create_auth_apikey(name: str, key: str, header: str = "Authorization"):
    """Create API key authentication."""
    from apiclient.config import AuthenticationConfig
    auth = AuthenticationConfig(
        name=name,
        auth_type="api_key",
        api_key=key,
        api_key_header=header,
    )
    config.save_auth_config(auth)
    print_success(f"Auth config '{name}' created")


@app.command()
def delete_auth(name: str):
    """Delete authentication config."""
    if config.delete_auth_config(name):
        print_success(f"Auth config '{name}' deleted")
    else:
        print_error(f"Auth config '{name}' not found")
        raise typer.Exit(1)


# ==================== GRAPHQL ====================
@app.command()
def list_graphql():
    """List GraphQL queries."""
    queries = config.load_graphql_queries()
    if not queries:
        print_info("No GraphQL queries found")
        return
    
    data = [[name, q.endpoint] for name, q in queries.items()]
    print_table(["Name", "Endpoint"], data)


@app.command()
def create_graphql(name: str, endpoint: str, query_text: str):
    """Create GraphQL query."""
    from apiclient.config import GraphQLQuery
    query = GraphQLQuery(
        name=name,
        endpoint=endpoint,
        query_text=query_text,
    )
    config.save_graphql_query(query)
    print_success(f"GraphQL query '{name}' created")


@app.command()
def execute_graphql(name: str):
    """Execute GraphQL query."""
    queries = config.load_graphql_queries()
    if name not in queries:
        print_error(f"Query '{name}' not found")
        raise typer.Exit(1)
    
    query = queries[name]
    
    try:
        import requests
        response = requests.post(
            query.endpoint,
            json={"query": query.query_text, "variables": query.variables or {}},
            headers={"Content-Type": "application/json"}
        )
        print_response(response.json())
    except Exception as e:
        print_error(f"Failed to execute query: {e}")
        raise typer.Exit(1)


@app.command()
def delete_graphql(name: str):
    """Delete GraphQL query."""
    if config.delete_graphql_query(name):
        print_success(f"GraphQL query '{name}' deleted")
    else:
        print_error(f"GraphQL query '{name}' not found")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
