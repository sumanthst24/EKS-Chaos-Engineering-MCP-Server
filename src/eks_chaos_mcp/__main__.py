#!/usr/bin/env python3
"""Entry point for the EKS Chaos MCP server."""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())