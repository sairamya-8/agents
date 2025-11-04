# AP WRIMS MCP Agent

This agent connects to the AP WRIMS (Andhra Pradesh Water Resources Information Management System) MCP server to provide agricultural and water resource data for Andhra Pradesh, India.

## Features

The agent provides access to:

- **Rainfall Data**: Actual, normal, and deviation data with natural language date support
- **Reservoir Information**: Water levels, capacity, metadata, and historical data
- **Soil Moisture**: Current soil moisture levels by location
- **Groundwater Levels**: Groundwater monitoring data from manual and DWLR sources
- **MI Tanks**: Minor irrigation tank data and time series
- **River Gauges**: River water level measurements
- **Lift Irrigation Schemes**: Information about lift irrigation projects
- **Water Conservation Structures**: Data on water conservation infrastructure

## Prerequisites

1. **ADK Setup**: Follow the [ADK quickstart guide](https://cloud.google.com/agent-engine/docs/quickstart)
2. **Python 3.9+**: Ensure you have Python 3.9 or higher
3. **MCP Server**: Access to the AP WRIMS MCP server (running via streamable HTTP)

## Configuration

### Environment Variables

Create a `.env` file in the parent directory or set these environment variables:

```bash
# Required: MCP server URL
export APWRIMS_MCP_URL="http://localhost:3000/mcp"

# Optional: Authentication token (if required by your MCP server)
export APWRIMS_AUTH_TOKEN="your-auth-token-here"

# Required: Google Cloud credentials (for Gemini API)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## Usage

### Option 1: Using `adk web` (Interactive UI)

1. Navigate to the parent directory:
   ```bash
   cd /Users/shaiksameer/Downloads/vassar/projects/agents/google_adk
   ```

2. Ensure your MCP server is running at the configured URL

3. Launch the ADK web interface:
   ```bash
   adk web
   ```

4. In the browser:
   - Select `apwrims_assistant` from the agent dropdown
   - Try example queries:
     - "What was the rainfall in Kurnool yesterday?"
     - "Show me reservoir data for Srisailam"
     - "What is the soil moisture in Anantapur district?"
     - "Get groundwater levels for Chittoor district for last month"

### Option 2: Programmatic Usage

Use the provided `example_usage.py` script:

```bash
cd /Users/shaiksameer/Downloads/vassar/projects/agents/google_adk/4_mcp_apwrims_agent
python example_usage.py
```

Or import and use in your own code:

```python
import asyncio
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the agent (make sure the parent directory is in your PYTHONPATH)
from google_adk.4_mcp_apwrims_agent.agent import root_agent

async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        state={}, app_name='apwrims_app', user_id='user123'
    )

    runner = Runner(
        app_name='apwrims_app',
        agent=root_agent,
        session_service=session_service,
    )

    query = "What was the rainfall in Kurnool yesterday?"
    content = types.Content(role='user', parts=[types.Part(text=query)])

    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    ):
        print(event)

asyncio.run(main())
```

## Example Queries

### Rainfall Data
```
"What was the rainfall in Kurnool district yesterday?"
"Show me rainfall data for Anantapur for last week"
"Compare rainfall in Visakhapatnam for last month vs normal"
"Get daily rainfall for Rayadurg mandal for the last 7 days"
```

### Reservoir Data
```
"Show me the current water level of Srisailam reservoir"
"What is the storage capacity of Nagarjuna Sagar?"
"Get reservoir metadata for Pothireddy Padu"
"Show me reservoir data for all major reservoirs in Krishna basin"
```

### Soil Moisture
```
"What is the soil moisture in Anantapur district?"
"Show soil moisture levels for Kurnool"
```

### Groundwater
```
"Get groundwater levels for Chittoor district for last month"
"Show me groundwater data for Prakasam district"
```

### MI Tanks
```
"List MI tanks in Rayadurg mandal with storage above 50%"
"Show me time series data for Gramadatla tank"
"Get MI tank alerts for Anantapur district"
```

## Date Handling

The agent supports natural language date references:

- **Relative days**: "today", "yesterday", "day before yesterday"
- **Relative weeks**: "last week", "last 2 weeks"
- **Relative months**: "last month", "last 3 months"
- **Relative years**: "last year", "last 2 years"
- **Specific dates**: "May 23", "June 1, 2025", "August 2023"
- **Week ranges**: "last month 1st week", "last month 2nd week"

The agent automatically converts these to the proper format required by the API.

## Location Types

When querying, you can specify different location types:

- `STATE`: Andhra Pradesh
- `DISTRICT`: e.g., Kurnool, Anantapur, Chittoor
- `MANDAL`: Sub-district level
- `VILLAGE`: Village level
- `BASIN`: River basin (e.g., Krishna, Godavari)
- `RESERVOIR`: Specific reservoir names
- `MI_TANK`: Minor irrigation tank names

## Deployment

For production deployment to Cloud Run, GKE, or Vertex AI Agent Engine, see the main ADK documentation on [MCP deployment patterns](https://cloud.google.com/agent-engine/docs/mcp-tools#deployment).

**Important**: Ensure your agent definition is synchronous (as shown in `agent.py`) for deployment compatibility.

## Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ADK Agent      │
│  (Gemini 2.5)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCPToolset     │
│  (HTTP Client)  │
└────────┬────────┘
         │
         ▼ (Streamable HTTP)
┌─────────────────┐
│  AP WRIMS       │
│  MCP Server     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WRIMS Data     │
│  APIs & DB      │
└─────────────────┘
```

## Troubleshooting

### Connection Errors

If you see MCP connection errors:

1. Verify the MCP server is running:
   ```bash
   curl http://localhost:3000/mcp
   ```

2. Check the `APWRIMS_MCP_URL` environment variable

3. Ensure network connectivity to the MCP server

### Authentication Errors

If you see 401/403 errors:

1. Verify your `APWRIMS_AUTH_TOKEN` is set correctly
2. Check token expiration
3. Confirm the token has necessary permissions

### Tool Discovery Issues

If the agent can't find tools:

1. Check MCP server logs for errors
2. Verify the server is implementing the MCP protocol correctly
3. Test the server's `/list_tools` endpoint

## Development

To modify or extend this agent:

1. Edit `agent.py` to change instructions or model
2. Add tool filters to limit exposed functionality
3. Modify connection parameters for different environments
4. Update `example_usage.py` for custom workflows

## References

- [ADK Documentation](https://cloud.google.com/agent-engine/docs)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AP WRIMS MCP Server Documentation](link-to-apwrims-docs)

## License

[Your license here]
