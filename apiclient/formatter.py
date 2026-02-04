"""Output formatting using Rich library."""

import json
from typing import Any, Dict
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel


console = Console()


def print_response(response: Dict[str, Any]):
    """Print a formatted API response."""
    if not response.get("success"):
        console.print(f"[bold red]Error:[/bold red] {response.get('error')}", style="red")
        return

    status_code = response.get("status_code")
    status_color = "green" if 200 <= status_code < 300 else "yellow" if status_code < 400 else "red"

    console.print(f"\n[bold {status_color}]Status: {status_code}[/bold {status_color}]")

    # Print headers
    if response.get("headers"):
        headers_table = Table(title="Response Headers", show_header=True)
        headers_table.add_column("Key", style="cyan")
        headers_table.add_column("Value", style="green")

        for key, value in sorted(response.get("headers", {}).items()):
            headers_table.add_row(key, str(value)[:100])

        console.print(headers_table)

    # Print body
    body = response.get("body")
    if body:
        if isinstance(body, dict) or isinstance(body, list):
            json_str = json.dumps(body, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title="Response Body", expand=False))
        else:
            console.print(Panel(str(body), title="Response Body", expand=False))


def print_request_info(method: str, url: str, headers: Dict = None, body: str = None):
    """Print formatted request information."""
    console.print(f"\n[bold cyan]→ {method}[/bold cyan] [underline]{url}[/underline]")

    if headers:
        for key, value in headers.items():
            console.print(f"  [dim]{key}:[/dim] {value}")

    if body:
        try:
            body_obj = json.loads(body)
            json_str = json.dumps(body_obj, indent=2)
            console.print(f"\n[dim]Body:[/dim]")
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
            console.print(syntax)
        except (json.JSONDecodeError, TypeError):
            console.print(f"\n[dim]Body:[/dim]\n{body}")


def print_table(title: str, rows: list, columns: list):
    """Print a formatted table."""
    table = Table(title=title, show_header=True)

    for col in columns:
        table.add_column(col, style="cyan")

    for row in rows:
        table.add_row(*row)

    console.print(table)


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")
