#!/usr/bin/env python3
"""Chaos Engineering EKS MCP Server implementation.

This module implements the Chaos engineering on EKS MCP Server, which provides tools for testing durability and resiliency of Amazon EKS clusters
and Kubernetes resources through the Model Context Protocol (MCP).

Environment Variables:
    AWS_REGION: AWS region to use for AWS API calls
    AWS_PROFILE: AWS profile to use for credentials
"""
import asyncio
import os
import sys
import logging

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError as e:
    print(f"MCP import error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    import boto3
except ImportError:
    print("boto3 not installed", file=sys.stderr)
    sys.exit(1)

try:
    from .pod_failure import inject_pod_failure, list_pods
    from .node_failure import simulate_node_failure
    from .az_failure import simulate_az_failure
except ImportError as e:
    print(f"Script import error: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize server
server = Server("chaos-engineering-eks")
logger.info("Server initialized successfully")

def initialize_aws_session():
    """Initialize AWS session with provided profile and region."""
    region = os.getenv('AWS_REGION', 'us-east-1')
    profile = os.getenv('AWS_PROFILE')
    
    session = boto3.Session(profile_name=profile, region_name=region)
    return session

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_pods_for_failure",
            description="List all pods in tabular format for selection",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulate_pod_failure",
            description="Inject pod failure for chaos testing",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Kubernetes namespace"},
                    "pod_name": {"type": "string", "description": "Pod name to delete"}
                },
                "required": ["namespace", "pod_name"]
            }
        ),
        Tool(
            name="simulate_node_failure",
            description="Simulate node failure by stopping EC2 instance with running pods",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulate_az_failure",
            description="Simulate AZ failure by terminating all instances in selected AZ",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
,

    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_pods_for_failure":
            result = list_pods()
            return [TextContent(type="text", text=result)]
        
        elif name == "simulate_pod_failure":
            namespace = arguments.get("namespace")
            pod_name = arguments.get("pod_name")
            result = inject_pod_failure(namespace, pod_name)
            return [TextContent(type="text", text=result)]
        
        elif name == "simulate_node_failure":
            result = simulate_node_failure()
            return [TextContent(type="text", text=result)]
        
        elif name == "simulate_az_failure":
            result = simulate_az_failure()
            return [TextContent(type="text", text=result)]
        

        

        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main function to run the MCP server."""
    logger.info("Starting MCP server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running...")
            await server.run(read_stream, write_stream, server.create_initialization_options())
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()