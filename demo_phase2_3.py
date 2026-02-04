#!/usr/bin/env python
"""
Demonstration script for ApiClient Pro - Phase 2 & 3 Features
Shows all new functionality including chains, templates, auth, mocks, and GraphQL
"""

import json
import time
import requests
from apiclient.config import (
    Config, RequestConfig, RequestChain, RequestTemplate,
    PerformanceMetric, AuthenticationConfig, MockEndpoint, GraphQLQuery
)
from apiclient.client import APIClient
from datetime import datetime

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_phase2_chaining():
    """Demonstrate Phase 2 - Request Chaining"""
    print_section("PHASE 2: REQUEST CHAINING")
    
    config = Config()
    
    # Create individual requests
    print("Creating requests...")
    req1 = RequestConfig(
        name="get_posts",
        method="GET",
        url="https://jsonplaceholder.typicode.com/posts?_limit=3"
    )
    config.save_request(req1)
    
    req2 = RequestConfig(
        name="create_comment",
        method="POST",
        url="https://jsonplaceholder.typicode.com/comments",
        body='{"postId": 1, "name": "Test", "email": "test@example.com", "body": "Great!"}'
    )
    config.save_request(req2)
    
    # Create a chain
    print("Creating request chain...")
    chain = RequestChain(
        name="posts_workflow",
        requests=["get_posts", "create_comment"],
        extract_rules=[{"from_request": 0, "response_path": "0.id", "variable_name": "first_post_id"}]
    )
    config.save_chain(chain)
    
    # List chains
    chains = config.load_chains()
    print(f"Saved chains: {list(chains.keys())}")
    
    # Show chain details
    if "posts_workflow" in chains:
        chain_data = chains["posts_workflow"]
        print(f"Chain: {chain_data.name}")
        print(f"  Requests: {chain_data.requests}")
        print(f"  Extract rules: {chain_data.extract_rules}")

def demo_phase2_templates():
    """Demonstrate Phase 2 - Request Templates"""
    print_section("PHASE 2: REQUEST TEMPLATES")
    
    config = Config()
    
    # Create templates
    print("Creating request templates...")
    templates = [
        RequestTemplate(
            name="rest_get",
            category="REST API",
            method="GET",
            base_url="https://api.example.com/v1/{resource}",
            description="Basic GET request template"
        ),
        RequestTemplate(
            name="github_api",
            category="GitHub",
            method="GET",
            base_url="https://api.github.com/{endpoint}",
            headers={"Accept": "application/vnd.github.v3+json"}
        ),
        RequestTemplate(
            name="graphql_query",
            category="GraphQL",
            method="POST",
            base_url="https://api.example.com/graphql",
            headers={"Content-Type": "application/json"}
        ),
    ]
    
    for template in templates:
        config.save_template(template)
    
    # List templates
    saved_templates = config.load_templates()
    print(f"\nSaved templates: {len(saved_templates)}")
    for name, template in saved_templates.items():
        print(f"  - {name} ({template.category}): {template.method}")

def demo_phase2_performance():
    """Demonstrate Phase 2 - Performance Monitoring"""
    print_section("PHASE 2: PERFORMANCE MONITORING")
    
    config = Config()
    
    # Record some metrics
    print("Recording performance metrics...")
    metrics = [
        PerformanceMetric(
            request_name="github_users",
            status_code=200,
            response_time=0.1255,
            response_size=1024,
            timestamp=datetime.now().isoformat()
        ),
        PerformanceMetric(
            request_name="json_posts",
            status_code=200,
            response_time=0.0873,
            response_size=2048,
            timestamp=datetime.now().isoformat()
        ),
        PerformanceMetric(
            request_name="linux_repo",
            status_code=404,
            response_time=0.0952,
            response_size=512,
            timestamp=datetime.now().isoformat()
        ),
    ]
    
    for metric in metrics:
        config.save_metric(metric)
    
    # Load and display metrics
    saved_metrics = config.load_metrics()
    print(f"\nRecorded metrics: {len(saved_metrics)}")
    
    if saved_metrics:
        times = [m.response_time for m in saved_metrics]
        successful = len([m for m in saved_metrics if m.status_code < 400])
        
        print(f"  Average response time: {sum(times)/len(times):.4f}s")
        print(f"  Min response time: {min(times):.4f}s")
        print(f"  Max response time: {max(times):.4f}s")
        print(f"  Success rate: {successful/len(saved_metrics)*100:.0f}%")

def demo_phase3_authentication():
    """Demonstrate Phase 3 - Authentication Helpers"""
    print_section("PHASE 3: AUTHENTICATION HELPERS")
    
    config = Config()
    
    # Create auth configs
    print("Creating authentication configurations...")
    auth_configs = [
        AuthenticationConfig(
            name="github_token",
            type="bearer",
            config={"token": "ghp_xxxxxxxxxxxxxxxxxxxx"}
        ),
        AuthenticationConfig(
            name="api_key",
            type="api_key",
            config={"header_name": "X-API-Key", "key": "sk_live_51234567890"}
        ),
        AuthenticationConfig(
            name="oauth_app",
            type="oauth2",
            config={
                "client_id": "client_id_here",
                "client_secret": "client_secret_here",
                "token_url": "https://auth.example.com/token"
            }
        ),
    ]
    
    for auth in auth_configs:
        config.save_auth_config(auth)
    
    # List auth configs
    saved_auth = config.load_auth_configs()
    print(f"\nSaved auth configs: {len(saved_auth)}")
    for name, auth in saved_auth.items():
        print(f"  - {name}: {auth.type}")

def demo_phase3_mocks():
    """Demonstrate Phase 3 - Mock Server"""
    print_section("PHASE 3: MOCK SERVER")
    
    config = Config()
    
    # Create mock endpoints
    print("Creating mock endpoints...")
    mocks = [
        MockEndpoint(
            name="user_response",
            path="/api/users/{id}",
            method="GET",
            response={"id": 1, "name": "John Doe", "email": "john@example.com"}
        ),
        MockEndpoint(
            name="posts_list",
            path="/api/posts",
            method="GET",
            response={"data": [{"id": 1, "title": "Post 1"}, {"id": 2, "title": "Post 2"}]}
        ),
        MockEndpoint(
            name="create_user",
            path="/api/users",
            method="POST",
            response={"id": 3, "name": "Jane Doe", "email": "jane@example.com"}
        ),
    ]
    
    for mock in mocks:
        config.save_mock_endpoint(mock)
    
    # List mock endpoints
    saved_mocks = config.load_mock_endpoints()
    print(f"\nConfigured mock endpoints: {len(saved_mocks)}")
    for name, mock in saved_mocks.items():
        print(f"  - {mock.method} {mock.path}")

def demo_phase3_graphql():
    """Demonstrate Phase 3 - GraphQL Support"""
    print_section("PHASE 3: GRAPHQL SUPPORT")
    
    config = Config()
    
    # Create GraphQL queries
    print("Creating GraphQL queries...")
    queries = [
        GraphQLQuery(
            name="get_users",
            endpoint="https://api.github.com/graphql",
            query="query { users { id name email } }"
        ),
        GraphQLQuery(
            name="user_repos",
            endpoint="https://api.github.com/graphql",
            query="""query($username: String!) {
                user(login: $username) {
                    name
                    repositories(first: 10) {
                        edges { node { name description } }
                    }
                }
            }""",
            variables={"username": "torvalds"}
        ),
        GraphQLQuery(
            name="create_post",
            endpoint="https://api.example.com/graphql",
            query="""mutation CreatePost($title: String!, $content: String!) {
                createPost(title: $title, content: $content) {
                    id title content createdAt
                }
            }""",
            variables={"title": "Hello", "content": "World"}
        ),
    ]
    
    for query in queries:
        config.save_graphql_query(query)
    
    # List GraphQL queries
    saved_queries = config.load_graphql_queries()
    print(f"\nSaved GraphQL queries: {len(saved_queries)}")
    for name, query in saved_queries.items():
        print(f"  - {name}: {query.endpoint}")

def demo_import_export():
    """Demonstrate Import/Export functionality"""
    print_section("IMPORT/EXPORT")
    
    config = Config()
    
    # Create some requests
    print("Creating sample requests for export...")
    requests_list = [
        RequestConfig(
            name="github_users",
            method="GET",
            url="https://api.github.com/users"
        ),
        RequestConfig(
            name="create_post",
            method="POST",
            url="https://jsonplaceholder.typicode.com/posts",
            headers={"Content-Type": "application/json"},
            body='{"title": "Test", "body": "Test post"}'
        ),
    ]
    
    for req in requests_list:
        config.save_request(req)
    
    # Show export formats
    saved = config.load_requests()
    print(f"\nExporting {len(saved)} requests...")
    
    # JSON format
    print("\nJSON Format:")
    print(json.dumps({name: r.dict() for name, r in saved.items()}, indent=2)[:200] + "...")
    
    # Postman format
    postman_export = {
        "info": {"name": "ApiClient Export", "version": "2.1.0"},
        "item": [
            {
                "name": name,
                "request": {
                    "method": r.method,
                    "url": {"raw": r.url}
                }
            }
            for name, r in saved.items()
        ]
    }
    print("\nPostman Format:")
    print(json.dumps(postman_export, indent=2)[:200] + "...")

def main():
    """Run all demonstrations"""
    print("\n" + "="*60)
    print("  APICLIENT PRO - PHASE 2 & 3 FEATURE DEMONSTRATION")
    print("="*60)
    
    # Phase 2
    demo_phase2_chaining()
    demo_phase2_templates()
    demo_phase2_performance()
    demo_import_export()
    
    # Phase 3
    demo_phase3_authentication()
    demo_phase3_mocks()
    demo_phase3_graphql()
    
    # Summary
    print_section("SUMMARY")
    print("✓ Phase 2 Features Implemented:")
    print("  - Request Chaining with variable passing")
    print("  - Request Templates for reusability")
    print("  - Performance Monitoring and analytics")
    print("  - Import/Export in multiple formats")
    
    print("\n✓ Phase 3 Features Implemented:")
    print("  - Authentication configurations (API Key, Bearer, OAuth2)")
    print("  - Mock Server endpoints")
    print("  - GraphQL query support")
    
    print("\n✓ Backends Ready:")
    print("  - FastAPI REST API at http://localhost:8000")
    print("  - Web Dashboard at http://localhost:8000/")
    print("  - CLI commands available via: python -m apiclient")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
