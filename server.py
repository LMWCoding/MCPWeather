import httpx
from fastmcp import FastMCP
import asyncio
import logging
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("SG-Weather")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Official data.gov.sg API endpoints
FORECAST_2HR_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast"
FORECAST_24HR_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
FORECAST_4DAY_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook"
TEMPERATURE_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"
RAINFALL_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
HUMIDITY_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/relative-humidity"
WIND_SPEED_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/wind-speed"
WIND_DIRECTION_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/wind-direction"
UV_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/uv-index"

# API timeout configuration
API_TIMEOUT = 20.0
MAX_RETRIES = 3
RETRY_DELAY = 2.0


@mcp.tool(
    name="get_sg_weather_forecast",  # Custom tool name for the LLM
    description="Fetch comprehensive weather forecasts including 2-hour, 24-hour, and 4-day forecasts for all areas in Singapore from the Singapore National Environment Agency (NEA).",  # Custom description
    tags={"weather", "singapore", "forecast"},  # Optional tags for organization/filtering
    meta={"version": "1.0", "lmw": "weather-team"},  # Custom metadata
)
async def get_sg_weather_forecast() -> str:
    """
    Fetches comprehensive weather forecasts from all available NEA forecast APIs including 2-hour, 24-hour, and 4-day forecasts.
    Returns forecasts for all areas in Singapore.
    """
    forecast_summary = "🌤️ Singapore Weather Forecasts\n"

    # Helper function to fetch data with retry logic
    async def fetch_with_retry(url, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e

    # Fetch 2-hour forecast
    try:
        data = await fetch_with_retry(FORECAST_2HR_API_URL)

        # Extract the actual data structure - it's nested under "data" key
        data_content = data.get("data", {})
        if not data_content:
            forecast_summary += "⚠️ 2-Hour Forecast: No data available\n"
        else:
            # Extract items array from the nested data
            items = data_content.get("items", [])
            if not items:
                forecast_summary += "⚠️ 2-Hour Forecast: No data available\n"
            else:
                latest = items[0]
                valid_period = latest.get("valid_period", {})
                # Use the text field for a more user-friendly period description
                period_text = valid_period.get("text", "Unknown period")
                timestamp = latest.get("timestamp", "Unknown timestamp")

                forecast_summary += "🌦️ 2-Hour Weather Forecast\n"
                forecast_summary += f"Valid period: {period_text}\n"
                forecast_summary += f"Forecast timestamp: {timestamp}\n"
                forecast_summary += "=====================================\n"

                # Loop through individual area forecasts
                forecasts = latest.get("forecasts", [])
                if not forecasts:
                    forecast_summary += "No detailed forecasts available.\n"
                else:
                    for forecast in forecasts:
                        area = forecast.get("area", "Unknown Area")
                        forecast_text = forecast.get("forecast", "No data")
                        forecast_summary += f"- {area}: {forecast_text}\n"
                forecast_summary += "\n"
    except Exception as e:
        forecast_summary += f"⚠️ 2-Hour Forecast: Error fetching data - {e}\n\n"

    # Fetch 24-hour forecast
    try:
        data = await fetch_with_retry(FORECAST_24HR_API_URL)

        # Extract the actual data structure - it's nested under "data" key
        data_content = data.get("data", {})
        if not data_content:
            forecast_summary += "⚠️ 24-Hour Forecast: No data available\n"
        else:
            # Extract records array from the nested data
            records = data_content.get("records", [])
            if not records:
                forecast_summary += "⚠️ 24-Hour Forecast: No data available\n"
            else:
                latest_record = records[0]
                valid_period = latest_record.get("general", {}).get("validPeriod", {})
                # Use the text field for a more user-friendly period description
                period_text = valid_period.get("text", "Unknown period")
                timestamp = latest_record.get("timestamp", "Unknown timestamp")

                forecast_summary += "🌤️ 24-Hour Weather Forecast\n"
                forecast_summary += f"Valid period: {period_text}\n"
                forecast_summary += f"Forecast timestamp: {timestamp}\n"
                forecast_summary += "=====================================\n"

                # Get general forecast information
                general = latest_record.get("general", {})
                forecast = general.get("forecast", {})
                forecast_text = forecast.get("text", "No data")
                forecast_summary += f"General forecast: {forecast_text}\n"

                # Get temperature range
                temperature = general.get("temperature", {})
                temp_low = temperature.get("low", "No data")
                temp_high = temperature.get("high", "No data")
                forecast_summary += f"Temperature range: {temp_low}°C to {temp_high}°C\n"

                # Get humidity range
                humidity = general.get("relativeHumidity", {})
                humidity_low = humidity.get("low", "No data")
                humidity_high = humidity.get("high", "No data")
                forecast_summary += f"Relative humidity: {humidity_low}% to {humidity_high}%\n"

                # Get wind information
                wind = general.get("wind", {})
                wind_direction = wind.get("direction", "No data")
                wind_speed = wind.get("speed", {})
                wind_speed_low = wind_speed.get("low", "No data")
                wind_speed_high = wind_speed.get("high", "No data")
                forecast_summary += f"Wind: {wind_direction}, {wind_speed_low} to {wind_speed_high} km/h\n"

                # Get period forecasts
                periods = latest_record.get("periods", [])
                if periods:
                    forecast_summary += "\nDetailed periods:\n"
                    for period in periods:
                        time_period = period.get("timePeriod", {})
                        time_text = time_period.get("text", "No time period")
                        regions = period.get("regions", {})
                        forecast_summary += f"  {time_text}:\n"
                        for region, region_forecast in regions.items():
                            region_text = region_forecast.get("text", "No forecast")
                            forecast_summary += f"    {region}: {region_text}\n"
                forecast_summary += "\n"
    except Exception as e:
        forecast_summary += f"⚠️ 24-Hour Forecast: Error fetching data - {e}\n\n"

    # Fetch 4-day forecast
    try:
        data = await fetch_with_retry(FORECAST_4DAY_API_URL)

        # Extract the actual data structure - it's nested under "data" key
        data_content = data.get("data", {})
        if not data_content:
            forecast_summary += "⚠️ 4-Day Forecast: No data available\n"
        else:
            # Extract records array from the nested data
            records = data_content.get("records", [])
            if not records:
                forecast_summary += "⚠️ 4-Day Forecast: No data available\n"
            else:
                latest_record = records[0]
                timestamp = latest_record.get("timestamp", "Unknown timestamp")
                forecasts = latest_record.get("forecasts", [])

                forecast_summary += "🌈 4-Day Weather Forecast\n"
                forecast_summary += f"Forecast timestamp: {timestamp}\n"
                forecast_summary += "=====================================\n"

                if not forecasts:
                    forecast_summary += "No detailed forecasts available.\n"
                else:
                    for i, forecast in enumerate(forecasts):
                        day = forecast.get("day", f"Day {i+1}")
                        forecast_info = forecast.get("forecast", {})
                        forecast_text = forecast_info.get("text", "No data")
                        temp_low = forecast.get("temperature", {}).get("low", "No data")
                        temp_high = forecast.get("temperature", {}).get("high", "No data")
                        humidity_low = forecast.get("relativeHumidity", {}).get("low", "No data")
                        humidity_high = forecast.get("relativeHumidity", {}).get("high", "No data")
                        wind_direction = forecast.get("wind", {}).get("direction", "No data")
                        wind_speed_low = forecast.get("wind", {}).get("speed", {}).get("low", "No data")
                        wind_speed_high = forecast.get("wind", {}).get("speed", {}).get("high", "No data")

                        forecast_summary += f"{day}:\n"
                        forecast_summary += f"  Forecast: {forecast_text}\n"
                        forecast_summary += f"  Temperature: {temp_low}°C to {temp_high}°C\n"
                        forecast_summary += f"  Humidity: {humidity_low}% to {humidity_high}%\n"
                        forecast_summary += f"  Wind: {wind_direction}, {wind_speed_low} to {wind_speed_high} km/h\n"
                        forecast_summary += "\n"
    except Exception as e:
        forecast_summary += f"⚠️ 4-Day Forecast: Error fetching data - {e}\n\n"

    return forecast_summary


@mcp.tool(
    name="get_sg_current_weather",  # Custom tool name for the LLM
    description="Fetch current weather data including temperature, rainfall, humidity, wind speed, and wind direction from all weather stations in Singapore from the Singapore National Environment Agency (NEA).",  # Custom description
    tags={
        "weather",
        "singapore",
        "temperature",
        "rainfall",
        "humidity",
        "wind",
    },  # Optional tags for organization/filtering
    meta={"version": "1.0", "lmw": "weather-team"},  # Custom metadata
)
async def get_sg_current_weather() -> str:
    """
    Fetches current weather data from all available NEA APIs including temperature, rainfall, humidity, wind speed, and wind direction.
    Returns comprehensive weather information from various weather stations.
    """
    weather_summary = "🌤️ Singapore Current Weather Conditions\n"

    # Helper function to fetch data with retry logic
    async def fetch_with_retry(url, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e

    # Fetch all station information first to create mapping
    station_name_map = {}
    try:
        data = await fetch_with_retry(TEMPERATURE_API_URL)
        temp_content = data.get("data", {})
        stations = temp_content.get("stations", [])

        for station in stations:
            station_id = station.get("id")
            station_name = station.get("name", "Unknown station")
            if station_id:
                station_name_map[station_id] = station_name
    except Exception as e:
        # If we can't get station names, we'll use IDs
        logger.warning(f"Failed to fetch station names: {e}")

    # Fetch temperature data
    try:
        data = await fetch_with_retry(TEMPERATURE_API_URL)

        # Extract temperature data
        temp_content = data.get("data", {})
        readings = temp_content.get("readings", [])

        if readings:
            latest_reading = readings[0]
            timestamp = latest_reading.get("timestamp", "Unknown timestamp")
            weather_summary += f"Data timestamp: {timestamp}\n"

            station_readings = latest_reading.get("data", [])
            weather_summary += "🌡️ Temperature (°C):\n"
            for reading in station_readings:
                station_id = reading.get("stationId", "Unknown station")
                temperature = reading.get("value", "No data")
                station_name = station_name_map.get(station_id, station_id)
                weather_summary += f"  - {station_name}: {temperature}°C\n"
    except Exception as e:
        weather_summary += f"Error fetching temperature data: {e}\n"

    # Fetch rainfall data
    try:
        data = await fetch_with_retry(RAINFALL_API_URL)

        # Extract rainfall data
        rain_content = data.get("data", {})
        readings = rain_content.get("readings", [])

        if readings:
            latest_reading = readings[0]
            station_readings = latest_reading.get("data", [])
            weather_summary += "🌧️ Rainfall (mm):\n"
            for reading in station_readings:
                station_id = reading.get("stationId", "Unknown station")
                rainfall = reading.get("value", "No data")
                station_name = station_name_map.get(station_id, station_id)
                weather_summary += f"  - {station_name}: {rainfall}mm\n"
    except Exception as e:
        weather_summary += f"Error fetching rainfall data: {e}\n"

    # Fetch humidity data
    try:
        data = await fetch_with_retry(HUMIDITY_API_URL)

        # Extract humidity data
        humidity_content = data.get("data", {})
        readings = humidity_content.get("readings", [])

        if readings:
            latest_reading = readings[0]
            station_readings = latest_reading.get("data", [])
            weather_summary += "💧 Humidity (%):\n"
            for reading in station_readings:
                station_id = reading.get("stationId", "Unknown station")
                humidity = reading.get("value", "No data")
                station_name = station_name_map.get(station_id, station_id)
                weather_summary += f"  - {station_name}: {humidity}%\n"
    except Exception as e:
        weather_summary += f"Error fetching humidity data: {e}\n"

    # Fetch wind speed data
    try:
        data = await fetch_with_retry(WIND_SPEED_API_URL)

        # Extract wind data
        wind_content = data.get("data", {})
        readings = wind_content.get("readings", [])

        if readings:
            latest_reading = readings[0]
            station_readings = latest_reading.get("data", [])
            weather_summary += "💨 Wind Speed (m/s):\n"
            for reading in station_readings:
                station_id = reading.get("stationId", "Unknown station")
                wind_speed = reading.get("value", "No data")
                station_name = station_name_map.get(station_id, station_id)
                weather_summary += f"  - {station_name}: {wind_speed}m/s\n"
    except Exception as e:
        weather_summary += f"Error fetching wind speed data: {e}\n"

    # Fetch wind direction data
    try:
        data = await fetch_with_retry(WIND_DIRECTION_API_URL)

        # Extract wind direction data
        wind_dir_content = data.get("data", {})
        readings = wind_dir_content.get("readings", [])

        if readings:
            latest_reading = readings[0]
            station_readings = latest_reading.get("data", [])
            weather_summary += "🔄 Wind Direction (degrees):\n"
            for reading in station_readings:
                station_id = reading.get("stationId", "Unknown station")
                wind_direction = reading.get("value", "No data")
                station_name = station_name_map.get(station_id, station_id)
                weather_summary += f"  - {station_name}: {wind_direction}°\n"
    except Exception as e:
        weather_summary += f"Error fetching wind direction data: {e}\n"

    # Skip UV index data as it requires authentication
    # UV API: https://api-open.data.gov.sg/v2/real-time/api/uv-index
    # weather_summary += "☀️ UV Index (not available - requires authentication)\n"

    return weather_summary


@mcp.tool(
    name="health_check",  # Custom tool name for the LLM
    description="Check the health status of the weather service.",  # Custom description
    tags={"health", "status"},  # Optional tags for organization/filtering
    meta={"version": "1.0", "lmw": "weather-team"},  # Custom metadata
)
async def health_check() -> str:
    """
    Check the health status of the weather service.
    Returns a simple health status message.
    """
    return "✅ Weather service is running and healthy"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3002)
