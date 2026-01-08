"""Weather API client for fetching weather data."""

import logging
from typing import Dict, Any, Optional

import httpx
from pydantic import BaseModel, Field

from .config import WeatherApiConfig

logger = logging.getLogger(__name__)


class WeatherData(BaseModel):
    """Structured weather data model."""
    
    location: str
    temperature: float
    feels_like: float
    description: str
    humidity: int
    pressure: int
    wind_speed: float
    units: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "location": self.location,
            "temperature": self.temperature,
            "feels_like": self.feels_like,
            "description": self.description,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "wind_speed": self.wind_speed,
            "units": self.units,
        }


class WeatherApiClient:
    """Client for interacting with weather APIs."""
    
    def __init__(self, config: WeatherApiConfig):
        """Initialize weather API client.
        
        Args:
            config: Weather API configuration.
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def get_current_weather(self, location: str) -> WeatherData:
        """Fetch current weather for a location.
        
        Args:
            location: City name, coordinates (lat,lon), or zip code.
            
        Returns:
            WeatherData object with current weather information.
            
        Raises:
            ValueError: If API key is not configured.
            httpx.HTTPError: If API request fails.
        """
        if not self.config.api_key or self.config.api_key.startswith('${'):
            raise ValueError(
                "Weather API key not configured. Set WEATHER_API_KEY environment variable."
            )
        
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Parse location format
        params = {
            "appid": self.config.api_key,
            "units": self.config.units,
        }
        
        # Check if location is coordinates (lat,lon format)
        if ',' in location and all(part.replace('.', '').replace('-', '').isdigit() 
                                   for part in location.split(',')):
            lat, lon = location.split(',')
            params["lat"] = lat.strip()
            params["lon"] = lon.strip()
        else:
            # Treat as city name or zip code
            params["q"] = location
        
        url = f"{self.config.base_url}/weather"
        
        logger.info(f"Fetching weather data for location: {location}")
        
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant data from OpenWeatherMap response
        return WeatherData(
            location=data.get("name", location),
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            description=data["weather"][0]["description"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            wind_speed=data["wind"]["speed"],
            units=self.config.units,
        )
    
    async def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Fetch weather forecast for a location.
        
        Args:
            location: City name, coordinates (lat,lon), or zip code.
            days: Number of days to forecast (max 5 for free tier).
            
        Returns:
            Dictionary with forecast data.
            
        Raises:
            ValueError: If API key is not configured.
            httpx.HTTPError: If API request fails.
        """
        if not self.config.api_key or self.config.api_key.startswith('${'):
            raise ValueError(
                "Weather API key not configured. Set WEATHER_API_KEY environment variable."
            )
        
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Parse location format
        params = {
            "appid": self.config.api_key,
            "units": self.config.units,
            "cnt": min(days * 8, 40),  # API returns 3-hour intervals, max 40
        }
        
        # Check if location is coordinates
        if ',' in location and all(part.replace('.', '').replace('-', '').isdigit() 
                                   for part in location.split(',')):
            lat, lon = location.split(',')
            params["lat"] = lat.strip()
            params["lon"] = lon.strip()
        else:
            params["q"] = location
        
        url = f"{self.config.base_url}/forecast"
        
        logger.info(f"Fetching forecast data for location: {location}")
        
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Format forecast data for easier consumption
        forecast_list = []
        for item in data["list"]:
            forecast_list.append({
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
            })
        
        return {
            "location": data["city"]["name"],
            "forecast": forecast_list,
            "units": self.config.units,
        }
