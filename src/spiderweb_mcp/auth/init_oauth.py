import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from spidergate.auth.clients import SCOPES, _get_auth_dir


def run_auth_flow() -> None:
    auth_dir = _get_auth_dir()
    cred_path = auth_dir / "credentials.json"
    token_path = auth_dir / "token.json"

    if not cred_path.exists():
        print(f"Error: Credentials file not found at {cred_path.resolve()}", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(cred_path),
        SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent")

    print("\n1. Open this URL in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Authorize Google account access.")
    code = input("3. Paste the authorization code here: ").strip()

    flow.fetch_token(code=code)
    creds = flow.credentials

    auth_dir.mkdir(parents=True, exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())

    print(f"\nSuccess! OAuth token saved to {token_path.resolve()}")


if __name__ == "__main__":
    run_auth_flow()
