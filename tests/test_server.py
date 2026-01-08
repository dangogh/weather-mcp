"""Tests for MCP server."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from weather_mcp.server import WeatherMcpServer
from weather_mcp.config import Config, WeatherApiConfig


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        weather_api=WeatherApiConfig(
            api_key="test_key",
            units="metric",
        )
    )


def test_server_initialization(test_config):
    """Test that server initializes correctly."""
    server = WeatherMcpServer(test_config)
    mcp_server = server.get_server()
    
    assert mcp_server is not None
    assert server.config == test_config


def test_server_name(test_config):
    """Test that server has correct name."""
    server = WeatherMcpServer(test_config)
    mcp_server = server.get_server()
    
    assert mcp_server.name == "weather-mcp"

