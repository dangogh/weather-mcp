"""Weather MCP Server implementation."""

import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from .config import Config
from .weather_client import WeatherApiClient

logger = logging.getLogger(__name__)


class WeatherMcpServer:
    """MCP Server for weather information."""
    
    def __init__(self, config: Config):
        """Initialize the weather MCP server.
        
        Args:
            config: Server configuration.
        """
        self.config = config
        self.server = Server("weather-mcp")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available weather tools."""
            return [
                Tool(
                    name="get_current_weather",
                    description=(
                        "Get current weather conditions for a location. "
                        "Location can be city name (e.g., 'London'), "
                        "coordinates as 'lat,lon' (e.g., '51.5074,-0.1278'), "
                        "or zip code with country (e.g., '10001,US')."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name, coordinates (lat,lon), or zip code",
                            },
                        },
                        "required": ["location"],
                    },
                ),
                Tool(
                    name="get_weather_forecast",
                    description=(
                        "Get weather forecast for a location up to 5 days ahead. "
                        "Returns forecasts in 3-hour intervals. "
                        "Location can be city name, coordinates, or zip code."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name, coordinates (lat,lon), or zip code",
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to forecast (1-5)",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 5,
                            },
                        },
                        "required": ["location"],
                    },
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
            """Handle tool calls for weather operations."""
            
            if name == "get_current_weather":
                location = arguments.get("location")
                if not location:
                    return [TextContent(
                        type="text",
                        text="Error: location parameter is required"
                    )]
                
                try:
                    async with WeatherApiClient(self.config.weather_api) as client:
                        weather = await client.get_current_weather(location)
                        
                        # Format response text
                        units_symbol = "°C" if self.config.weather_api.units == "metric" else "°F"
                        wind_units = "m/s" if self.config.weather_api.units == "metric" else "mph"
                        
                        response_text = (
                            f"Current weather in {weather.location}:\n"
                            f"Temperature: {weather.temperature}{units_symbol} "
                            f"(feels like {weather.feels_like}{units_symbol})\n"
                            f"Conditions: {weather.description}\n"
                            f"Humidity: {weather.humidity}%\n"
                            f"Pressure: {weather.pressure} hPa\n"
                            f"Wind Speed: {weather.wind_speed} {wind_units}"
                        )
                        
                        return [TextContent(type="text", text=response_text)]
                        
                except ValueError as e:
                    logger.error(f"Configuration error: {e}")
                    return [TextContent(type="text", text=f"Configuration error: {str(e)}")]
                except Exception as e:
                    logger.error(f"Error fetching weather: {e}")
                    return [TextContent(type="text", text=f"Error: {str(e)}")]
            
            elif name == "get_weather_forecast":
                location = arguments.get("location")
                days = arguments.get("days", 3)
                
                if not location:
                    return [TextContent(
                        type="text",
                        text="Error: location parameter is required"
                    )]
                
                try:
                    async with WeatherApiClient(self.config.weather_api) as client:
                        forecast_data = await client.get_forecast(location, days)
                        
                        # Format response text
                        units_symbol = "°C" if self.config.weather_api.units == "metric" else "°F"
                        wind_units = "m/s" if self.config.weather_api.units == "metric" else "mph"
                        
                        response_lines = [f"Weather forecast for {forecast_data['location']}:\n"]
                        
                        for item in forecast_data["forecast"]:
                            response_lines.append(
                                f"{item['datetime']}: {item['temperature']}{units_symbol} "
                                f"(feels like {item['feels_like']}{units_symbol}), "
                                f"{item['description']}, "
                                f"humidity {item['humidity']}%, "
                                f"wind {item['wind_speed']} {wind_units}"
                            )
                        
                        return [TextContent(type="text", text="\n".join(response_lines))]
                        
                except ValueError as e:
                    logger.error(f"Configuration error: {e}")
                    return [TextContent(type="text", text=f"Configuration error: {str(e)}")]
                except Exception as e:
                    logger.error(f"Error fetching forecast: {e}")
                    return [TextContent(type="text", text=f"Error: {str(e)}")]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    def get_server(self) -> Server:
        """Get the underlying MCP server instance."""
        return self.server
