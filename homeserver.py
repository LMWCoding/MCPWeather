import logging
from typing import Literal

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Home Automation")

CONTROL_ENDPOINT = "http://192.168.1.154:1880/control"
API_TIMEOUT = 20.0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="control_home_device",
    description=(
        "Turn a home device on or off by room name and device name. "
        "Supported rooms: master, boy, girl, living, and study. "
        "Supported devices: Lights, TV, and Fan."
    ),
    tags={"home", "automation", "device"},
    meta={"version": "1.0", "lmw": "home-automation-team"},
)
async def control_home_device(
    room: Literal["master", "boy", "girl", "living", "study"],
    device: Literal["Lights", "TV", "Fan"],
    action: Literal["on", "off"],
) -> str:
    """Control one home device in a named room."""
    payload = {
        "room": room,
        "device": device,
        "action": action,
    }

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(CONTROL_ENDPOINT, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        logger.error("Home control endpoint returned %s", error.response.status_code)
        return (
            f"Home device control failed: endpoint returned "
            f"HTTP {error.response.status_code}."
        )
    except httpx.RequestError as error:
        logger.error("Home control endpoint request failed: %s", error)
        return f"Home device control failed: {error}"

    try:
        result = response.json()
    except ValueError:
        result = response.text

    return f"Home device control request succeeded: {result}"


@mcp.tool(
    name="health_check",
    description="Check the health status of the home automation service.",
    tags={"health", "status"},
    meta={"version": "1.0", "lmw": "home-automation-team"},
)
async def health_check() -> str:
    """Check the health status of the home automation service."""
    return "Home automation service is running and healthy"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3002, path="/mcp")
