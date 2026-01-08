"""Weather MCP Server package."""

__version__ = "1.0.0"

from .server import WeatherMcpServer
from .config import load_config

__all__ = ["WeatherMcpServer", "load_config"]
