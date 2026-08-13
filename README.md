# MCP Weather Service

A FastMCP-based weather service for Singapore that provides current weather conditions and forecasts from the National Environment Agency (NEA) APIs.

## Features

- **Current Weather Data**: Temperature, rainfall, humidity, wind speed, and wind direction from all weather stations
- **Weather Forecasts**: 2-hour, 24-hour, and 4-day forecasts for all areas in Singapore
- **Comprehensive API Integration**: All data from official NEA weather APIs
- **Robust Error Handling**: Retry logic, timeouts, and graceful degradation
- **Async Implementation**: Efficient concurrent API calls

## Available Tools

### 1. `get_sg_weather_forecast`
Fetches comprehensive weather forecasts including:
- 2-hour weather forecast for all areas in Singapore
- 24-hour weather forecast with detailed period breakdowns
- 4-day weather outlook with temperature, humidity, and wind information

### 2. `get_sg_current_weather`
Fetches current weather data from all weather stations:
- Temperature readings (°C)
- Rainfall measurements (mm)
- Humidity levels (%)
- Wind speed (m/s)
- Wind direction (degrees)

### 3. `health_check`
Simple health status check for the weather service.

## API Endpoints Used

- **2-Hour Forecast**: `https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast`
- **24-Hour Forecast**: `https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast`
- **4-Day Outlook**: `https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook`
- **Temperature**: `https://api-open.data.gov.sg/v2/real-time/api/air-temperature`
- **Rainfall**: `https://api-open.data.gov.sg/v2/real-time/api/rainfall`
- **Humidity**: `https://api-open.data.gov.sg/v2/real-time/api/relative-humidity`
- **Wind Speed**: `https://api-open.data.gov.sg/v2/real-time/api/wind-speed`
- **Wind Direction**: `https://api-open.data.gov.sg/v2/real-time/api/wind-direction`

## Installation

```bash
# Install dependencies
pip install -e .
```

## Usage

Start the server:
```bash
python server.py
```

The service will be available at `http://localhost:3002`

## Robustness Features

- **Retry Logic**: Automatic retries for failed API calls (3 attempts with 2s delay)
- **Timeout Handling**: Configurable timeouts (20s) for all API requests
- **Error Recovery**: Graceful degradation when data is unavailable
- **Logging**: Comprehensive logging for debugging and monitoring
- **Health Check**: Built-in health status endpoint

## Requirements

- Python 3.13+
- FastMCP 3.4.7+
- httpx 0.28.1+

## License

MIT