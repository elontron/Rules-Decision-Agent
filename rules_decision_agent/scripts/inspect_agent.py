
import sys
import inspect

def print_module(name, module):
    print(f"\n--- {name} ---")
    print(dir(module))
    if hasattr(module, '__path__'):
        print("Path:", module.__path__)

try:
    import google.adk
    print_module("google.adk", google.adk)
    
    import google.adk.agents
    print_module("google.adk.agents", google.adk.agents)
    
    import google.adk.tools
    print_module("google.adk.tools", google.adk.tools)
    
    # Check for MCP
    import mcp
    print_module("mcp", mcp)
    
except ImportError as e:
    print(f"Error importing adk: {e}")

try:
    import a2a
    print_module("a2a", a2a)
    import a2a.server.apps
    print_module("a2a.server.apps", a2a.server.apps)
except ImportError as e:
    print(f"Error importing a2a: {e}")
