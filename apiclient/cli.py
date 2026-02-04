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


if __name__ == "__main__":
    app()
