
from fastmcp import FastMCP
from spidergate.auth.clients import get_google_services


def register_tasks_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_google_tasks(show_completed: bool = False) -> str:
        """Lists tasks from the primary task list including status and ID."""
        _, tasks = get_google_services()
        tasklists = tasks.tasklists().list().execute().get("items", [])
        if not tasklists:
            return "No task lists found."

        primary_list_id = tasklists[0]["id"]
        items = tasks.tasks().list(
            tasklist=primary_list_id,
            showCompleted=show_completed,
            showHidden=show_completed
        ).execute().get("items", [])

        if not items:
            return "No tasks found."

        output = []
        for t in items:
            status_box = "[x]" if t.get("status") == "completed" else "[ ]"
            due = f" (Due: {t.get('due')})" if t.get("due") else ""
            output.append(f"{status_box} [{t.get('id')}] {t.get('title', 'Untitled')}{due}")
        return "\n".join(output)

    @mcp.tool()
    def add_google_task(title: str, notes: str = "", due_iso: str = None) -> str:
        """Creates a new Google Task. due_iso in RFC3339 format (e.g. '2026-08-12T00:00:00.000Z')."""
        _, tasks = get_google_services()
        tasklists = tasks.tasklists().list().execute().get("items", [])
        primary_list_id = tasklists[0]["id"]

        body = {"title": title, "notes": notes}
        if due_iso:
            body["due"] = due_iso

        result = tasks.tasks().insert(tasklist=primary_list_id, body=body).execute()
        return f"Task created: '{result.get('title')}' (ID: {result.get('id')})"

    @mcp.tool()
    def complete_google_task(task_id: str) -> str:
        """Marks a Google Task as completed using its Task ID."""
        _, tasks = get_google_services()
        tasklists = tasks.tasklists().list().execute().get("items", [])
        primary_list_id = tasklists[0]["id"]

        task = tasks.tasks().get(tasklist=primary_list_id, taskId=task_id).execute()
        task["status"] = "completed"
        result = tasks.tasks().update(tasklist=primary_list_id, taskId=task_id, body=task).execute()
        return f"Task marked as completed: '{result.get('title')}'"

    @mcp.tool()
    def delete_google_task(task_id: str) -> str:
        """Deletes a Google Task by its Task ID."""
        _, tasks = get_google_services()
        tasklists = tasks.tasklists().list().execute().get("items", [])
        primary_list_id = tasklists[0]["id"]

        try:
            tasks.tasks().delete(tasklist=primary_list_id, taskId=task_id).execute()
            return f"Task '{task_id}' successfully deleted."
        except Exception as e:
            return f"Error deleting task '{task_id}': {str(e)}"