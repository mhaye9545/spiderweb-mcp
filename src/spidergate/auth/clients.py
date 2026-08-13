import os
from pathlib import Path
from typing import Tuple
from github import Github, Auth
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]


def _get_auth_dir() -> Path:
    env_path = os.environ.get("AUTH_DIR_PATH")
    if env_path:
        return Path(env_path)
    # Default to parent root auth/ folder
    return Path.cwd() / "auth"


def get_google_services() -> Tuple[Resource, Resource]:
    """Initializes and returns Google Calendar and Tasks API service clients."""
    auth_dir = _get_auth_dir()
    token_path = auth_dir / "token.json"

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
        else:
            raise RuntimeError(
                f"Valid Google OAuth token not found at '{token_path}'. Run 'spidergate-auth' or 'python -m spidergate.auth.init_oauth' first."
            )

    calendar_service = build("calendar", "v3", credentials=creds)
    tasks_service = build("tasks", "v1", credentials=creds)
    return calendar_service, tasks_service


def get_github_client() -> Github:
    """Initializes and returns the PyGithub client."""
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("Environment variable 'GITHUB_PERSONAL_ACCESS_TOKEN' is not configured.")
    return Github(auth=Auth.Token(token))