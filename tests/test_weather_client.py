"""Tests for weather API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from weather_mcp.weather_client import WeatherApiClient, WeatherData
from weather_mcp.config import WeatherApiConfig


@pytest.fixture
def api_config():
    """Create test API configuration."""
    return WeatherApiConfig(
        api_key="test_api_key",
        base_url="https://api.example.com",
        units="metric",
        timeout=10,
    )


@pytest.fixture
def mock_weather_response():
    """Mock OpenWeatherMap API response."""
    return {
        "name": "London",
        "main": {
            "temp": 15.5,
            "feels_like": 14.2,
            "humidity": 72,
            "pressure": 1013,
        },
        "weather": [
            {"description": "partly cloudy"}
        ],
        "wind": {
            "speed": 3.5
        }
    }


@pytest.fixture
def mock_forecast_response():
    """Mock OpenWeatherMap forecast API response."""
    return {
        "city": {"name": "London"},
        "list": [
            {
                "dt_txt": "2024-01-15 12:00:00",
                "main": {
                    "temp": 16.0,
                    "feels_like": 15.0,
                    "humidity": 70,
                },
                "weather": [{"description": "clear sky"}],
                "wind": {"speed": 2.5},
            },
            {
                "dt_txt": "2024-01-15 15:00:00",
                "main": {
                    "temp": 17.5,
                    "feels_like": 16.5,
                    "humidity": 65,
                },
                "weather": [{"description": "few clouds"}],
                "wind": {"speed": 3.0},
            },
        ]
    }


@pytest.mark.asyncio
async def test_get_current_weather_by_city(api_config, mock_weather_response):
    """Test fetching current weather by city name."""
    with patch('weather_mcp.weather_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value=mock_weather_response)
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        async with WeatherApiClient(api_config) as client:
            weather = await client.get_current_weather("London")
        
        assert weather.location == "London"
        assert weather.temperature == 15.5
        assert weather.feels_like == 14.2
        assert weather.description == "partly cloudy"
        assert weather.humidity == 72
        assert weather.pressure == 1013
        assert weather.wind_speed == 3.5


@pytest.mark.asyncio
async def test_get_current_weather_by_coordinates(api_config, mock_weather_response):
    """Test fetching current weather by coordinates."""
    with patch('weather_mcp.weather_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value=mock_weather_response)
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        async with WeatherApiClient(api_config) as client:
            weather = await client.get_current_weather("51.5074,-0.1278")
        
        # Verify coordinates were passed as params
        call_args = mock_client.get.call_args
        assert "lat" in call_args[1]["params"]
        assert "lon" in call_args[1]["params"]


@pytest.mark.asyncio
async def test_get_forecast(api_config, mock_forecast_response):
    """Test fetching weather forecast."""
    with patch('weather_mcp.weather_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value=mock_forecast_response)
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        async with WeatherApiClient(api_config) as client:
            forecast = await client.get_forecast("London", days=3)
        
        assert forecast["location"] == "London"
        assert len(forecast["forecast"]) == 2
        assert forecast["forecast"][0]["temperature"] == 16.0
        assert forecast["forecast"][0]["description"] == "clear sky"


@pytest.mark.asyncio
async def test_missing_api_key():
    """Test that missing API key raises appropriate error."""
    config = WeatherApiConfig(api_key="${WEATHER_API_KEY}")
    
    async with WeatherApiClient(config) as client:
        with pytest.raises(ValueError, match="API key not configured"):
            await client.get_current_weather("London")


@pytest.mark.asyncio
async def test_weather_data_to_dict():
    """Test WeatherData conversion to dictionary."""
    weather = WeatherData(
        location="London",
        temperature=15.5,
        feels_like=14.2,
        description="partly cloudy",
        humidity=72,
        pressure=1013,
        wind_speed=3.5,
        units="metric",
    )
    
    data = weather.to_dict()
    
    assert data["location"] == "London"
    assert data["temperature"] == 15.5
    assert data["humidity"] == 72
    assert data["units"] == "metric"


@pytest.mark.asyncio
async def test_parse_location_params_coordinates():
    """Test location parameter parsing with valid coordinates."""
    config = WeatherApiConfig(api_key="test_key", units="metric")
    client = WeatherApiClient(config)
    
    # Test positive coordinates
    params = client._parse_location_params("51.5074,-0.1278")
    assert "lat" in params
    assert "lon" in params
    assert params["lat"] == "51.5074"
    assert params["lon"] == "-0.1278"
    
    # Test negative coordinates
    params = client._parse_location_params("-33.8688,151.2093")
    assert params["lat"] == "-33.8688"
    assert params["lon"] == "151.2093"
    
    # Test invalid coordinates fall back to text query
    params = client._parse_location_params("not,coordinates")
    assert "q" in params
    assert params["q"] == "not,coordinates"
