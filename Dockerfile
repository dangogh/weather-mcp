FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config.yaml .

# Create a non-root user to run the application
RUN useradd -m -u 1000 weatheruser && \
    chown -R weatheruser:weatheruser /app

USER weatheruser

# Set Python path to include src directory
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Default to stdio mode, but can be overridden
ENV SERVER_MODE=stdio

# Expose HTTP port (only used in HTTP mode)
EXPOSE 8080

# Run the server
CMD ["python", "-m", "weather_mcp"]
