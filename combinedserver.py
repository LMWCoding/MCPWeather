from fastmcp import FastMCP

import homeserver
import weatherserver

mcp = FastMCP("MCP Weather and Home Automation")
mcp.mount(weatherserver.mcp, namespace="weather")
mcp.mount(homeserver.mcp, namespace="home")


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3002, path="/mcp")
