#!/usr/bin/env python3
import json
from fastmcp import FastMCP
import inspect

# Create the FastMCP server instance.
mcp = FastMCP("BasicMCPRegistry")

# Global registry for tools.
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

# --- MCP Tools ---
@mcp.tool()
def list_tools() -> str:
    """Lists all registered tool names."""
    tool_names = [tool["name"] for tool in AVAILABLE_TOOLS]
    return json.dumps({"tools": tool_names}, indent=2)

@mcp.tool()
def fetch_tool_description(tool_name: str) -> str:
    """
    Returns the description and expected parameters for a given tool name.
    """
    for tool in AVAILABLE_TOOLS:
        if tool["name"].lower() == tool_name.lower():
            # Extract parameter names from the function signature
            signature = inspect.signature(tool["function"])
            params = [
                {"name": name, "type": str(param.annotation).replace("<class '", "").replace("'>", "")}
                for name, param in signature.parameters.items()
            ]

            return json.dumps({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": params
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
