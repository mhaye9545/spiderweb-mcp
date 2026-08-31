"""Tests for meta diagnostic tools."""

import asyncio
from fastmcp import FastMCP
from spiderweb_mcp.tools.meta import register_meta_tools


def test_get_gateway_status():
    mcp = FastMCP("test-spiderweb")
    register_meta_tools(mcp)
    tool = asyncio.run(mcp.get_tool("get_gateway_status"))
    assert tool is not None

    status = tool.fn()
    assert "Spiderweb MCP Gateway: ONLINE" in status
    assert "Working Directory:" in status
    assert "Python Runtime:" in status
