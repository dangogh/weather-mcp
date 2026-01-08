from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="weather-mcp",
    version="1.0.0",
    author="Weather MCP Contributors",
    description="MCP server providing weather information via OpenWeatherMap API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dangogh/weather-mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.27.0",
        "PyYAML>=6.0.0",
        "uvicorn>=0.30.0",
        "fastapi>=0.110.0",
        "sse-starlette>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weather-mcp=weather_mcp.__main__:cli",
        ],
    },
)
