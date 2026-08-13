from fastmcp import FastMCP
from spidergate.tools import register_all_tools

mcp = FastMCP("SpidergateCentralGateway")

# Register all sub-modules
register_all_tools(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()