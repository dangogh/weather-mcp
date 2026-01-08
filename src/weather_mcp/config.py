"""Configuration management for Weather MCP server."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class HttpConfig(BaseModel):
    """HTTP server configuration."""
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)


class ServerConfig(BaseModel):
    """Server configuration."""
    
    mode: str = Field(default="stdio", pattern="^(stdio|http)$")
    http: HttpConfig = Field(default_factory=HttpConfig)


class WeatherApiConfig(BaseModel):
    """Weather API configuration."""
    
    provider: str = Field(default="openweathermap")
    base_url: str = Field(default="https://api.openweathermap.org/data/2.5")
    api_key: str = Field(default="")
    units: str = Field(default="metric", pattern="^(metric|imperial|standard)$")
    timeout: int = Field(default=10)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class Config(BaseSettings):
    """Main application configuration."""
    
    model_config = {"env_nested_delimiter": "__", "case_sensitive": False}
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    weather_api: WeatherApiConfig = Field(default_factory=WeatherApiConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file and environment variables.
    
    Environment variables take precedence over config file values.
    Supports variable substitution in config file using ${VAR_NAME} syntax.
    
    Args:
        config_path: Path to YAML config file. Defaults to config.yaml in repo root.
        
    Returns:
        Config object with loaded configuration.
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config.yaml")
    
    config_dict: Dict[str, Any] = {}
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f) or {}
        
        # Substitute environment variables in config values
        config_dict = _substitute_env_vars(config_dict)
    
    # Override with environment variable for API key if present
    api_key = os.environ.get('WEATHER_API_KEY')
    if api_key:
        if 'weather_api' not in config_dict:
            config_dict['weather_api'] = {}
        config_dict['weather_api']['api_key'] = api_key
    
    return Config(**config_dict)


def _substitute_env_vars(config: Any) -> Any:
    """Recursively substitute ${VAR_NAME} with environment variable values."""
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
        var_name = config[2:-1]
        return os.environ.get(var_name, config)
    return config
