
import datetime
from fastmcp import FastMCP
from spiderweb_mcp.auth.clients import get_google_services


def _resolve_calendar_id(cal_service, calendar_name_or_id: str) -> str:
    """Resolves human-readable calendar names into official Google Calendar IDs."""
    if not calendar_name_or_id or calendar_name_or_id.lower() in ["primary", "default", "standard", "hauptkalender"]:
        return "primary"

    calendar_list = cal_service.calendarList().list().execute().get("items", [])

    # Exact summary match
    for c in calendar_list:
        if c.get("summary", "").lower() == calendar_name_or_id.lower():
            return c["id"]

    # Partial summary match
    for c in calendar_list:
        if calendar_name_or_id.lower() in c.get("summary", "").lower():
            return c["id"]

    # ID match fallback
    for c in calendar_list:
        if c.get("id") == calendar_name_or_id:
            return c["id"]

    return calendar_name_or_id


def register_calendar_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_upcoming_calendar_events(days_ahead: int = 14, max_results: int = 30) -> str:
        """Retrieves upcoming events across all active Google Calendars within the next X days."""
        cal, _ = get_google_services()
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        now = now_dt.isoformat()
        time_max = (now_dt + datetime.timedelta(days=days_ahead)).isoformat()

        calendar_list = cal.calendarList().list().execute().get("items", [])
        all_events = []

        for c in calendar_list:
            cal_id = c["id"]
            cal_name = c.get("summary", "Untitled")

            if not c.get("selected", True):
                continue

            try:
                events_result = cal.events().list(
                    calendarId=cal_id,
                    timeMin=now,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()

                for event in events_result.get("items", []):
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    all_events.append({
                        "start": start,
                        "title": event.get("summary", "Untitled"),
                        "id": event.get("id"),
                        "calendar": cal_name
                    })
            except Exception:
                continue

        if not all_events:
            return f"No events found within the next {days_ahead} days."

        all_events.sort(key=lambda x: x["start"])

        output = [f"- [{ev['calendar']}] {ev['start']}: {ev['title']} (ID: {ev['id']})" for ev in all_events[:max_results]]
        return "\n".join(output)

    @mcp.tool()
    def add_calendar_event(
        summary: str,
        start_iso: str,
        end_iso: str,
        calendar_name: str = "primary",
        description: str = "",
        location: str = ""
    ) -> str:
        """Creates a new calendar event.
        - calendar_name: Name of target calendar (e.g. 'Family', 'primary').
        - Timestamps: ISO-8601 format (e.g. '2026-08-12T14:00:00+02:00').
        """
        cal, _ = get_google_services()
        target_cal_id = _resolve_calendar_id(cal, calendar_name)

        event_body = {
            "summary": summary,
            "description": description,
            "location": location,
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso},
        }

        try:
            event = cal.events().insert(calendarId=target_cal_id, body=event_body).execute()
            return f"Event created in calendar '{calendar_name}': '{event.get('summary')}' (ID: {event.get('id')}) - Link: {event.get('htmlLink')}"
        except Exception as e:
            return f"Error creating calendar event: {str(e)}"

    @mcp.tool()
    def delete_calendar_event(event_id: str, calendar_name: str = "primary") -> str:
        """Deletes a calendar event by its ID, with automatic scan fallback."""
        cal, _ = get_google_services()
        target_cal_id = _resolve_calendar_id(cal, calendar_name)

        try:
            cal.events().delete(calendarId=target_cal_id, eventId=event_id).execute()
            return f"Event '{event_id}' successfully deleted from '{calendar_name}'."
        except Exception:
            # Fallback scan across all accessible calendars
            calendar_list = cal.calendarList().list().execute().get("items", [])
            for c in calendar_list:
                try:
                    cal.events().delete(calendarId=c["id"], eventId=event_id).execute()
                    return f"Event '{event_id}' found and deleted from calendar '{c.get('summary')}'."
                except Exception:
                    continue

            return f"Error: Event '{event_id}' could not be located or deleted in any calendar."