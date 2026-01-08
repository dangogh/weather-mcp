# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather information using the OpenWeatherMap API. This server primarily runs in stdio mode (the standard for MCP servers) with an experimental HTTP API mode for testing.

## Features

- **MCP Protocol Support**: Full stdio mode support for MCP clients
- **HTTP API Mode**: Experimental simple HTTP API for testing
- **Current Weather**: Get current weather conditions for any location
- **Weather Forecast**: Get weather forecasts up to 5 days ahead
- **Location Flexibility**: Support for city names, coordinates (lat,lon), and zip codes
- **Docker Support**: Containerized deployment with docker-compose
- **Configurable**: YAML-based configuration with environment variable support
- **Well Tested**: Comprehensive test suite with pytest

## Prerequisites

- Python 3.11 or higher
- OpenWeatherMap API key (free tier available at [OpenWeatherMap](https://openweathermap.org/api))
- Docker (optional, for containerized deployment)

## Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/dangogh/weather-mcp.git
cd weather-mcp

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using Docker

```bash
# Build the Docker image
docker build -t weather-mcp .

# Or use docker-compose (see Docker section below)
```

## Configuration

The server uses a YAML configuration file (`config.yaml`) with the following structure:

```yaml
server:
  mode: stdio  # or 'http'
  http:
    host: 0.0.0.0
    port: 8080

weather_api:
  provider: openweathermap
  base_url: https://api.openweathermap.org/data/2.5
  api_key: ${WEATHER_API_KEY}  # Set via environment variable
  units: metric  # or 'imperial' or 'standard'
  timeout: 10

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Environment Variables

- `WEATHER_API_KEY`: Your OpenWeatherMap API key (required)
- `SERVER_MODE`: Override server mode (optional, defaults to config file)

## Usage

### Running in stdio mode

```bash
# Set your API key
export WEATHER_API_KEY="your_api_key_here"

# Run the server
python -m weather_mcp

# Or use the CLI command
weather-mcp
```

### Running in HTTP mode (Experimental)

**Note**: HTTP mode provides a simple REST API for testing. For production MCP usage, use stdio mode.

```bash
# Update config.yaml to set mode: http, or use environment variable
export WEATHER_API_KEY="your_api_key_here"
export SERVER_MODE=http

python -m weather_mcp
```

The HTTP server will start on `http://localhost:8080` with the following endpoints:
- `GET /`: Server information
- `GET /health`: Health check
- `POST /weather/current`: Get current weather (JSON: `{"location": "London"}`)
- `POST /weather/forecast`: Get forecast (JSON: `{"location": "London", "days": 3}`)

### Using with Docker

#### Stdio mode:
```bash
# Set your API key in .env file
echo "WEATHER_API_KEY=your_api_key_here" > .env

# Run with docker-compose
docker-compose --profile stdio run weather-mcp-stdio
```

#### HTTP mode:
```bash
# Run HTTP server
docker-compose --profile http up weather-mcp-http

# The server will be available at http://localhost:8080
```

## Available Tools

### get_current_weather

Get current weather conditions for a location.

**Parameters:**
- `location` (string, required): City name, coordinates (lat,lon), or zip code

**Example:**
```json
{
  "location": "London"
}
```

**Response includes:**
- Temperature and "feels like" temperature
- Weather description
- Humidity percentage
- Atmospheric pressure
- Wind speed

### get_weather_forecast

Get weather forecast for a location up to 5 days ahead.

**Parameters:**
- `location` (string, required): City name, coordinates (lat,lon), or zip code
- `days` (integer, optional): Number of days to forecast (1-5, default: 3)

**Example:**
```json
{
  "location": "New York",
  "days": 3
}
```

**Response includes:**
- Forecast data in 3-hour intervals
- Same weather details as current weather for each interval

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src/weather_mcp --cov-report=html
```

### Code Structure

```
weather-mcp/
├── src/
│   └── weather_mcp/
│       ├── __init__.py
│       ├── __main__.py       # Entry point
│       ├── config.py          # Configuration management
│       ├── server.py          # MCP server implementation
│       ├── weather_client.py  # Weather API client
│       └── http_server.py     # HTTP streaming server
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_weather_client.py
│   └── test_server.py
├── config.yaml                # Configuration file
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker compose configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── setup.py                   # Package setup
└── README.md                  # This file
```

## API Reference

### OpenWeatherMap API

This server uses the OpenWeatherMap API. Key features:
- **Free Tier**: 60 calls/minute, 1,000,000 calls/month
- **Current Weather**: Real-time weather data
- **5-Day Forecast**: Weather predictions in 3-hour intervals
- **Location Support**: City names, coordinates, zip codes

Get your free API key at: https://openweathermap.org/api

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### API Key Issues

If you see "API key not configured" errors:
1. Ensure `WEATHER_API_KEY` environment variable is set
2. Check that the key is valid and active on OpenWeatherMap
3. Verify the key is not expired (free tier keys don't expire but can be revoked)

### Connection Issues

If you encounter connection errors:
1. Check your internet connection
2. Verify OpenWeatherMap API is accessible from your location
3. Check if you've exceeded rate limits (60 calls/minute for free tier)

### Docker Issues

If Docker containers fail to start:
1. Ensure Docker and docker-compose are installed
2. Check that port 8080 is not already in use (for HTTP mode)
3. Verify the API key is properly set in the environment

## Support

For issues and questions:
- Open an issue on GitHub: https://github.com/dangogh/weather-mcp/issues
- Check existing issues for solutions
