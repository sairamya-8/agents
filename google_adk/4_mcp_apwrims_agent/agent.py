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
    "APWRIMS_MCP_URL", "http://localhost:9081/mcp"
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
        "Water resource assistant for Andhra Pradesh. "
        "Provides data on rainfall, reservoirs, soil moisture, groundwater, "
        "and irrigation systems."
    ),
    instruction=(
        "You are a helpful assistant specialized in water "
        "resource management for Andhra Pradesh, India. You have access to "
        "the AP WRIMS (Water Resources Information Management System) data.\n\n"
        "You can help users with:\n"
        "- Rainfall data (actual, normal, deviation) for locations\n"
        "- Reservoir information and metadata\n"
        "- Soil moisture levels\n"
        "- Groundwater levels\n"
        "- MI tank (minor irrigation) data\n"
        "- River gauge measurements\n"
        "- Lift irrigation schemes\n"
        "- Water conservation structures\n\n"
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
