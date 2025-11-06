"""
Advanced MCP Agent with Code Execution - V2
===========================================
Fixed version that includes MCP server code inline for code execution environment.
"""

from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor


# Create the agent with stateful code execution
root_agent = LlmAgent(
    name="AdvancedMCPAgent",
    model="gemini-2.5-flash",
    code_executor=BuiltInCodeExecutor(stateful=True),
    description=(
        "Advanced agent that uses code execution to efficiently interact with "
        "MCP servers via progressive disclosure pattern."
    ),
    instruction='''You are an advanced agent that interacts with MCP servers using code execution.

IMPORTANT: Before answering any questions, you MUST run this setup code ONCE to initialize the MCP tools:

# === MCP CLIENT AND SERVER SETUP (RUN THIS FIRST) ===
class MCPClient:
    """Dummy MCP client with sample data"""
    _documents = dict(
        abc123=dict(
            title="Q4 Sales Meeting Transcript",
            content="Sales Meeting - Q4 2025\\nKey points: Revenue target $2.5M, new product launch Dec 15...",
            metadata=dict(created="2025-11-01", owner="sarah.chen@company.com")
        )
    )
    _sheets = dict(
        sheet001=dict(
            title="Sales Leads Q4",
            rows=[
                dict(ID="001", Name="Acme Corp", Contact="john@acme.com", Status="pending", Value=50000),
                dict(ID="002", Name="TechStart Inc", Contact="sarah@techstart.com", Status="active", Value=75000),
                dict(ID="003", Name="Global Solutions", Contact="mike@global.com", Status="pending", Value=100000),
            ]
        )
    )

    @classmethod
    def call_tool(cls, server, tool, params):
        handler_name = "_handle_" + server + "_" + tool
        handler = getattr(cls, handler_name, None)
        if not handler:
            raise ValueError("Unknown tool: " + server + "." + tool)
        return handler(params)

    @classmethod
    def _handle_google_drive_get_document(cls, params):
        doc_id = params.get("document_id")
        doc = cls._documents.get(doc_id)
        if not doc:
            return dict(error="Document " + doc_id + " not found")
        return doc

    @classmethod
    def _handle_google_drive_get_sheet(cls, params):
        sheet_id = params.get("sheet_id")
        sheet = cls._sheets.get(sheet_id)
        if not sheet:
            return dict(error="Sheet " + sheet_id + " not found")
        return sheet.get("rows", [])

    @classmethod
    def _handle_google_drive_list_files(cls, params):
        files = []
        for doc_id, doc in cls._documents.items():
            files.append(dict(id=doc_id, name=doc["title"], type="document"))
        for sheet_id, sheet in cls._sheets.items():
            files.append(dict(id=sheet_id, name=sheet["title"], type="spreadsheet"))
        return dict(files=files)

    @classmethod
    def _handle_salesforce_query(cls, params):
        return dict(records=[
            dict(Id="00Q001", Name="John Doe", Email="john@example.com", Company="Acme"),
            dict(Id="00Q002", Name="Jane Smith", Email="jane@example.com", Company="TechStart")
        ])

    @classmethod
    def _handle_salesforce_create_record(cls, params):
        return dict(success=True, id="00Q999", message="Created record")

    @classmethod
    def _handle_salesforce_update_record(cls, params):
        record_id = params.get("record_id", "unknown")
        return dict(success=True, id=record_id, message="Updated record " + record_id)

# Create global client instance
mcp_client = MCPClient()

# Google Drive tools
def gdrive_get_document(document_id):
    """Get a document from Google Drive"""
    return mcp_client.call_tool("google_drive", "get_document", dict(document_id=document_id))

def gdrive_get_sheet(sheet_id):
    """Get a spreadsheet from Google Drive"""
    return mcp_client.call_tool("google_drive", "get_sheet", dict(sheet_id=sheet_id))

def gdrive_list_files():
    """List files in Google Drive"""
    return mcp_client.call_tool("google_drive", "list_files", dict())

# Salesforce tools
def sf_query(soql_query):
    """Query Salesforce records"""
    return mcp_client.call_tool("salesforce", "query", dict(query=soql_query))

def sf_create_record(object_type, data):
    """Create a Salesforce record"""
    return mcp_client.call_tool("salesforce", "create_record",
                                dict(object_type=object_type, data=data))

def sf_update_record(object_type, record_id, data):
    """Update a Salesforce record"""
    return mcp_client.call_tool("salesforce", "update_record",
                                dict(object_type=object_type, record_id=record_id, data=data))

print("✓ MCP tools initialized successfully!")
print("Available tools:")
print("  Google Drive: gdrive_get_document(), gdrive_get_sheet(), gdrive_list_files()")
print("  Salesforce: sf_query(), sf_create_record(), sf_update_record()")

# === END SETUP CODE ===

After running the setup code above, you can use the MCP tools like this:

EXAMPLES:

1. List Google Drive files:
files = gdrive_list_files()
print("Files:", files)

2. Get a document:
doc = gdrive_get_document("abc123")
print("Title:", doc["title"])
print("Content:", doc["content"][:100])

3. Get and filter spreadsheet (CONTEXT-EFFICIENT):
rows = gdrive_get_sheet("sheet001")
pending = [r for r in rows if r.get("Status") == "pending"]
print("Found", len(pending), "pending leads out of", len(rows), "total")
for lead in pending:
    print("  -", lead["Name"], ":", lead["Value"])

4. Query Salesforce:
leads = sf_query("SELECT Id, Name FROM Lead")
print("Salesforce leads:", leads)

5. Create Salesforce record:
result = sf_create_record("Lead", dict(Name="New Company", Email="contact@newco.com"))
print("Created:", result)

6. Privacy-preserving data transfer:
doc = gdrive_get_document("abc123")
result = sf_update_record("Lead", "00Q001", dict(Notes=doc["content"]))
print("Updated:", result["message"])

IMPORTANT WORKFLOW:
1. FIRST: Always run the setup code above to initialize MCP tools
2. THEN: Use the tools (gdrive_*, sf_*) to accomplish your task
3. Filter and process data in code before showing results to keep context clean

Remember: The setup code creates a stateful environment, so you only need to run it once per session!
''',
)
