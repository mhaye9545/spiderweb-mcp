from fastmcp import FastMCP
from spiderweb_mcp.tools import register_all_tools

mcp = FastMCP("SpiderwebCentralGateway")

# Register all sub-modules
register_all_tools(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()