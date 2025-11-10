"""
AP WRIMS MCP Agent
==================
This agent connects to the AP WRIMS (Andhra Pradesh Water Resources Information
Management System) MCP server to provide agricultural and water resource data.

The agent can:
- Retrieve rainfall data for locations
- Get soil moisture information
- Access reservoir data and metadata
- Query groundwater levels
- Get MI tank information
- Access river gauge data
- And more...
"""


import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

# Configure MCP server URL from environment variable or use default
# Set APWRIMS_MCP_URL environment variable to override
MCP_SERVER_URL = os.environ.get(
    "APWRIMS_MCP_URL", "http://localhost:8081/mcp"
)

# Optional: Configure authentication headers if needed
MCP_AUTH_HEADERS = {}
if os.environ.get("APWRIMS_AUTH_TOKEN"):
    MCP_AUTH_HEADERS["Authorization"] = (
        f"Bearer {os.environ.get('APWRIMS_AUTH_TOKEN')}"
    )

root_agent = Agent(
    name="apwrims_assistant",
    model="gemini-2.5-flash",
    description=(
        "Apaims agricultural resource assistant for Andhra Pradesh. "
        "Provides data on weather forecast, pest forewarning, crop sown area, pest surveillance, market prices, and query cassandra tool"
    ),
    instruction=(
        "You are a helpful assistant specialized in agricultural data "
        "resource management for Andhra Pradesh, India. You have access to "
        "the AP AIMS (Agricultural Information Management System) data.\n\n"
        "You can help users with:\n"
        "- weather forecast(rainfall, temperature, wind, humidity) for locations\n"
        "- pest forewarning\n"
        "- crop sown area\n"
        "- pest surveillance\n"
        "- market prices\n"
        "- query cassandra tool (yield, msp, exports, cost of cultivation, cost of production, harvest prices, wholesale prices)\n"
        "When users ask about dates:\n"
        "- Support natural language like 'today', 'yesterday', 'last week', "
        "'last month'\n"
        "- Always convert these to proper date formats (YYYYMMDD for daily, "
        "YYYYMM for monthly, YYYY for yearly)\n"
        "- For location queries, be specific about location names and types "
        "(DISTRICT, MANDAL, VILLAGE, etc.)\n\n"
        "Provide clear, helpful responses with relevant data and context."
    ),
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
                headers=MCP_AUTH_HEADERS,
            ),
            # Optional: Filter to specific tools if needed
            # Uncomment and modify to limit tools exposed to the agent
            # tool_filter=[
            #     'getRainfallData',
            #     'getReservoirData',
            #     'getSoilMoistureData',
            #     'getGroundwaterLevels',
            # ]
        )
    ],
)
