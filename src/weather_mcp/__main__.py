"""Main entry point for the Weather MCP server."""

import asyncio
import logging
import sys
from pathlib import Path

from mcp.server.stdio import stdio_server

from .config import load_config
from .server import WeatherMcpServer
from .http_server import run_http_server


def setup_logging(config):
    """Configure logging based on configuration."""
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format=config.logging.format,
    )


async def run_stdio_server(config):
    """Run MCP server in stdio mode.
    
    Args:
        config: Server configuration.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting Weather MCP server in stdio mode")
    
    weather_server = WeatherMcpServer(config)
    mcp_server = weather_server.get_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


async def main():
    """Main entry point for the server."""
    # Load configuration
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    config = load_config(config_path)
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    
    # Run server based on configured mode
    if config.server.mode == "stdio":
        await run_stdio_server(config)
    elif config.server.mode == "http":
        await run_http_server(config)
    else:
        logger.error(f"Unknown server mode: {config.server.mode}")
        sys.exit(1)


def cli():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
