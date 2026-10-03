import os, sys
from mcp.server.fastmcp import FastMCP

label = sys.argv[1] if len(sys.argv) > 1 else "unknown"
mcp = FastMCP(f"lab-{label}")

@mcp.tool()
def whoami() -> str:
    """Report which workspace's server answered, and whether a token is present."""
    has_token = "yes" if os.environ.get("LAB_TOKEN") else "no"
    return f"Hello from the {label} server. Token present: {has_token}"

@mcp.resource("lab://policy")
def policy() -> str:
    """This client's data-handling policy (read-only)."""
    return f"{label}: no client data leaves this workspace."

if __name__ == "__main__":
    mcp.run()  # stdio transport by default