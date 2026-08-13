import httpx
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("SG-Weather")

# Official data.gov.sg API endpoint for 2-hour forecast
# Note: data.gov.sg doesn't have a direct API endpoint for 2-hour forecasts
# We'll use the NEA (National Environment Agency) API which is the official source
NEA_API_URL = "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast"


@mcp.tool(
    name="get_sg_2hr_forecast",  # Custom tool name for the LLM
    description="Fetch the latest authoritative 2-hour weather forecast for all areas in Singapore from the Singapore National Environment Agency (NEA).",  # Custom description
    tags={"weather", "singapore"},  # Optional tags for organization/filtering
    meta={"version": "1.0", "lmw": "weather-team"},  # Custom metadata
)
async def get_sg_2hr_forecast() -> str:
    """
    Fetches the latest authoritative 2-hour weather forecast for all areas in Singapore from the Singapore National Environment Agency (NEA).
    Returns the general forecast, period, and neighborhood-level forecasts.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Fetch data from the official NEA API
            response = await client.get(NEA_API_URL, timeout=20.0)
            response.raise_for_status()
            data = response.json()

            # Extract the actual data structure - it's nested under "data" key
            data_content = data.get("data", {})
            if not data_content:
                return "Error: No weather forecast data available right now."

            # Extract items array from the nested data
            items = data_content.get("items", [])
            if not items:
                return "Error: No weather forecast data available right now."

            latest = items[0]
            valid_period = latest.get("valid_period", {})
            # Use the text field for a more user-friendly period description
            period_text = valid_period.get("text", "Unknown period")
            timestamp = latest.get("timestamp", "Unknown timestamp")

            forecast_summary = "🌦️ Singapore 2-Hour Weather Forecast\n"
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

            return forecast_summary

        except httpx.HTTPStatusError as e:
            return (
                f"Error: Unable to reach NEA API. Status code: {e.response.status_code}"
            )
        except Exception as e:
            return f"An unexpected error occurred: {e!s}"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3002)
