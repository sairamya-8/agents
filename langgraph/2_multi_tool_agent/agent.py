"""
LangGraph Multi-Tool Agent with Weather and Time Tools
Demonstrates using multiple tools with LangGraph.
"""

import os
import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Define tools
@tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city: The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


@tool
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Bind tools to the LLM
tools = [get_weather, get_current_time]
llm_with_tools = llm.bind_tools(tools)


# Define the agent state
class AgentState(MessagesState):
    """State of the agent with message history."""
    pass


# Define the agent node
def call_model(state: AgentState):
    """Call the LLM with tools."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Define routing function
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine whether to continue to tools or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return "end"


# Create the graph
def create_agent():
    """Create and compile the LangGraph agent."""

    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    # Set entry point
    workflow.add_edge(START, "agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# Create the agent
agent = create_agent()


def run_agent(user_input: str, thread_id: str = "1"):
    """Run the agent with a user input.

    Args:
        user_input: The user's question or request
        thread_id: The conversation thread ID for memory

    Returns:
        The agent's response
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Invoke the agent
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    # Get the last message
    last_message = result["messages"][-1]
    return last_message.content


# Main execution
if __name__ == "__main__":
    print("LangGraph Weather & Time Agent")
    print("=" * 50)
    print("Ask me about the weather or time in cities!")
    print("Type 'quit' to exit\n")

    thread_id = "main_conversation"

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = run_agent(user_input, thread_id)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
