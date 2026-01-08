"""HTTP streaming server for MCP over Server-Sent Events."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import ServerSentEvent
from mcp.server.sse import SseServerTransport

from .server import WeatherMcpServer
from .config import Config

logger = logging.getLogger(__name__)


def create_http_app(config: Config) -> FastAPI:
    """Create FastAPI application for HTTP streaming MCP server.
    
    Args:
        config: Server configuration.
        
    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Weather MCP Server",
        description="MCP server providing weather information via OpenWeatherMap API",
        version="1.0.0",
    )
    
    # Create MCP server instance
    weather_server = WeatherMcpServer(config)
    mcp_server = weather_server.get_server()
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "weather-mcp"}
    
    @app.post("/sse")
    async def handle_sse(request: Request):
        """Handle MCP over Server-Sent Events.
        
        This endpoint provides streaming MCP communication over HTTP using SSE.
        Clients should POST JSON-RPC messages and receive responses via SSE.
        """
        async with SseServerTransport("/messages") as transport:
            # Initialize transport with request/response handling
            await transport.handle_post_message(request, mcp_server)
            
            async def event_generator():
                """Generate SSE events from MCP responses."""
                async for message in transport.get_response_stream():
                    yield ServerSentEvent(data=message)
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
            )
    
    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "service": "Weather MCP Server",
            "version": "1.0.0",
            "protocol": "MCP over SSE",
            "endpoints": {
                "health": "/health",
                "sse": "/sse (POST)",
            },
        }
    
    return app


async def run_http_server(config: Config):
    """Run the HTTP streaming MCP server.
    
    Args:
        config: Server configuration.
    """
    import uvicorn
    
    app = create_http_app(config)
    
    logger.info(
        f"Starting HTTP server on {config.server.http.host}:{config.server.http.port}"
    )
    
    uvicorn_config = uvicorn.Config(
        app,
        host=config.server.http.host,
        port=config.server.http.port,
        log_level=config.logging.level.lower(),
    )
    
    server = uvicorn.Server(uvicorn_config)
    await server.serve()
