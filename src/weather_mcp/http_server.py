"""HTTP server for basic weather API (Experimental).

Note: Full MCP over SSE support requires additional ASGI integration.
This provides a simple HTTP API for testing. For production MCP usage,
use stdio mode which is the standard for MCP servers.
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .weather_client import WeatherApiClient
from .config import Config

logger = logging.getLogger(__name__)


class WeatherRequest(BaseModel):
    """Weather request model."""
    location: str


class ForecastRequest(BaseModel):
    """Forecast request model."""
    location: str
    days: int = 3


def create_http_app(config: Config) -> FastAPI:
    """Create FastAPI application for weather HTTP API.
    
    Note: This is a simplified HTTP API, not full MCP over SSE.
    For MCP protocol support, use stdio mode.
    
    Args:
        config: Server configuration.
        
    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Weather MCP Server - HTTP API",
        description="Simple HTTP API for weather information (Experimental)",
        version="1.0.0",
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "weather-mcp"}
    
    @app.post("/weather/current")
    async def get_current_weather(request: WeatherRequest):
        """Get current weather for a location.
        
        Args:
            request: Weather request with location.
            
        Returns:
            Current weather data.
        """
        try:
            async with WeatherApiClient(config.weather_api) as client:
                weather = await client.get_current_weather(request.location)
                return weather.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/weather/forecast")
    async def get_weather_forecast(request: ForecastRequest):
        """Get weather forecast for a location.
        
        Args:
            request: Forecast request with location and days.
            
        Returns:
            Weather forecast data.
        """
        try:
            async with WeatherApiClient(config.weather_api) as client:
                forecast = await client.get_forecast(request.location, request.days)
                return forecast
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "service": "Weather MCP Server - HTTP API",
            "version": "1.0.0",
            "note": "This is a simplified HTTP API. For MCP protocol, use stdio mode.",
            "endpoints": {
                "health": "/health",
                "current_weather": "/weather/current (POST)",
                "forecast": "/weather/forecast (POST)",
            },
        }
    
    return app


async def run_http_server(config: Config):
    """Run the HTTP weather API server.
    
    Note: This runs a simple HTTP API, not full MCP over SSE.
    For MCP protocol support, use stdio mode instead.
    
    Args:
        config: Server configuration.
    """
    import uvicorn
    
    app = create_http_app(config)
    
    logger.info(
        f"Starting HTTP server on {config.server.http.host}:{config.server.http.port}"
    )
    logger.info("Note: Running simple HTTP API mode. For MCP protocol, use stdio mode.")
    
    uvicorn_config = uvicorn.Config(
        app,
        host=config.server.http.host,
        port=config.server.http.port,
        log_level=config.logging.level.lower(),
    )
    
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


