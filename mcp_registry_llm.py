#!/usr/bin/env python3
import json
from fastmcp import FastMCP

mcp = FastMCP("MCPRegistry-LLM")
AVAILABLE_TOOLS = []

def register_tool(func):
    """
    Decorator to register a function as a tool.
    Uses the function's name as the tool name and its docstring as the description.
    """
    description = func.__doc__ or "No description provided."
    tool_entry = {
        "name": func.__name__,
        "description": description.strip(),
        "function": func,
    }
    AVAILABLE_TOOLS.append(tool_entry)
    return func

# --- Tool Definitions ---
@register_tool
def add(a: int, b: int) -> int:
    """Adds two numbers together. Usage: add(a, b)."""
    return a + b

@register_tool
def subtract(a: int, b: int) -> int:
    """Subtracts the second number from the first. Usage: subtract(a, b)."""
    return a - b

@register_tool
def greet(name: str) -> str:
    """Greets a person by name. Usage: greet(name)."""
    return f"Hello, {name}!"

def call_llm_simulation(query: str) -> dict:
    """
    Simulates an external LLM call.
    For demonstration purposes, this function returns the tool with the highest
    occurrence of query keywords. In a real implementation, this would call an LLM API.
    """
    # For simplicity, choose the first tool whose name is found in the query.
    for tool in AVAILABLE_TOOLS:
        if tool["name"].lower() in query.lower():
            return {
                "selected_tool": tool["name"],
                "description": tool["description"],
                "note": "Simulated LLM response."
            }
    # Fallback: return the first tool in the registry.
    if AVAILABLE_TOOLS:
        tool = AVAILABLE_TOOLS[0]
        return {
            "selected_tool": tool["name"],
            "description": tool["description"],
            "note": "Simulated LLM fallback response."
        }
    return {"error": "No tools available."}

@mcp.tool()
def select_best_tool(query: str) -> str:
    """
    Selects the best tool based on a simulated LLM call.
    Returns a JSON string with the selected tool's name and description.
    """
    result = call_llm_simulation(query)
    return json.dumps(result, indent=2)

# Also include the basic MCP tools.
@mcp.tool()
def list_tools() -> str:
    """Lists all registered tool names."""
    tool_names = [tool["name"] for tool in AVAILABLE_TOOLS]
    return json.dumps({"tools": tool_names}, indent=2)

@mcp.tool()
def fetch_tool_description(tool_name: str) -> str:
    """Returns the description for a given tool name."""
    for tool in AVAILABLE_TOOLS:
        if tool["name"].lower() == tool_name.lower():
            return json.dumps({
                "name": tool["name"],
                "description": tool["description"]
            }, indent=2)
    return json.dumps({"error": f"Tool '{tool_name}' not found."}, indent=2)

@mcp.tool()
def use_tool(tool_name: str, params: str) -> str:
    """
    Executes the specified tool with the provided parameters.
    Parameters:
      - tool_name: The name of the tool to execute.
      - params: JSON string representing a list of positional arguments.
    Returns:
      A JSON string with the tool's result or an error message.
    """
    import json
    for tool in AVAILABLE_TOOLS:
        if tool["name"].lower() == tool_name.lower():
            try:
                args = json.loads(params)
                result = tool["function"](*args)
                return json.dumps({"tool": tool["name"], "result": result}, indent=2)
            except Exception as e:
                return json.dumps({"error": f"Error executing tool: {str(e)}"}, indent=2)
    return json.dumps({"error": f"Tool '{tool_name}' not found."}, indent=2)

if __name__ == "__main__":
    mcp.run()
