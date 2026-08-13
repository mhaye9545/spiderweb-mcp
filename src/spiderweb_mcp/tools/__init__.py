from .calendar import register_calendar_tools
from .tasks import register_tasks_tools
from .github import register_github_tools
from .meta import register_meta_tools


def register_all_tools(mcp) -> None:
    register_calendar_tools(mcp)
    register_tasks_tools(mcp)
    register_github_tools(mcp)
    register_meta_tools(mcp)
