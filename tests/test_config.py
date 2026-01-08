"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest

from weather_mcp.config import load_config, Config


def test_load_default_config():
    """Test loading configuration with defaults."""
    config = Config()
    
    assert config.server.mode == "stdio"
    assert config.server.http.host == "0.0.0.0"
    assert config.server.http.port == 8080
    assert config.weather_api.provider == "openweathermap"
    assert config.weather_api.units == "metric"
    assert config.logging.level == "INFO"


def test_load_config_from_yaml():
    """Test loading configuration from YAML file."""
    yaml_content = """
server:
  mode: http
  http:
    host: 127.0.0.1
    port: 9090

weather_api:
  api_key: test_key_123
  units: imperial

logging:
  level: DEBUG
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        
        assert config.server.mode == "http"
        assert config.server.http.host == "127.0.0.1"
        assert config.server.http.port == 9090
        assert config.weather_api.api_key == "test_key_123"
        assert config.weather_api.units == "imperial"
        assert config.logging.level == "DEBUG"
    finally:
        os.unlink(temp_path)


def test_env_var_substitution():
    """Test environment variable substitution in config."""
    yaml_content = """
weather_api:
  api_key: ${TEST_API_KEY}
"""
    
    # Set environment variable
    os.environ['TEST_API_KEY'] = 'env_test_key'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        assert config.weather_api.api_key == 'env_test_key'
    finally:
        os.unlink(temp_path)
        del os.environ['TEST_API_KEY']


def test_env_var_override():
    """Test that environment variables override config file."""
    yaml_content = """
weather_api:
  api_key: file_key
"""
    
    os.environ['WEATHER_API_KEY'] = 'env_override_key'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    try:
        config = load_config(temp_path)
        # Environment variable should override file value
        assert config.weather_api.api_key == 'env_override_key'
    finally:
        os.unlink(temp_path)
        del os.environ['WEATHER_API_KEY']


def test_invalid_server_mode():
    """Test that invalid server mode raises validation error."""
    with pytest.raises(Exception):  # Pydantic validation error
        Config(server={"mode": "invalid_mode"})


def test_invalid_units():
    """Test that invalid units raise validation error."""
    with pytest.raises(Exception):  # Pydantic validation error
        Config(weather_api={"units": "invalid_units"})
