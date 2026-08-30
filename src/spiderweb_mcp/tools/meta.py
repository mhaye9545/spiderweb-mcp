import os
import sys
from fastmcp import FastMCP


def register_meta_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_gateway_status() -> str:
        """Returns runtime diagnostics and status metadata for the gateway."""
        return (
            f"Spiderweb MCP Gateway: ONLINE\n"
            f"Working Directory: {os.getcwd()}\n"
            f"Python Runtime: {sys.version.split()[0]}"
        )