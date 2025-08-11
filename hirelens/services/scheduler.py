# hirelens/services/scheduler.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential

from hirelens.configs.settings import settings

# Full Calendar scope so we can create events + Meet links
SCOPES = ["https://www.googleapis.com/auth/calendar"]

TOKEN_PATH = Path(settings.BASE_DIR) / ".google_token.json"  # cache refresh token locally


def _get_creds() -> Credentials:
    """
    Desktop OAuth flow:
      - Use credentials file specified in settings.GOOGLE_OAUTH_CREDS
      - Cache user token in .google_token.json so you don't need to re-consent
    """
    creds: Optional[Credentials] = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # will auto-refresh via google-auth transport
            pass
        else:
            # IMPORTANT: Use a Desktop OAuth client JSON (it must contain "installed": {...})
            flow = InstalledAppFlow.from_client_secrets_file(str(settings.GOOGLE_OAUTH_CREDS), SCOPES)
            # Opens a browser window on first run; loopback redirect is handled automatically
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def _service():
    creds = _get_creds()
    return build("calendar", "v3", credentials=creds)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def schedule_meet(
    interviewer_email: str,
    candidate_email: str,
    start_iso: str,   # "2025-08-11T11:00:00"
    end_iso: str,     # "2025-08-11T11:30:00"
    title: str,
    description: Optional[str],
    timezone: str,
) -> dict:
    """
    Create a Calendar event with a Google Meet link and invite both attendees.
    Returns dict with eventId/htmlLink/meetLink.
    """
    # basic validation (FastAPI will also validate types)
    try:
        datetime.fromisoformat(start_iso)
        datetime.fromisoformat(end_iso)
    except Exception:
        raise ValueError("start_iso and end_iso must be ISO datetimes, e.g. 2025-08-11T11:00:00")

    svc = _service()

    event_body = {
        "summary": title,
        "description": description or "",
        "start": {"dateTime": start_iso, "timeZone": timezone},
        "end": {"dateTime": end_iso, "timeZone": timezone},
        "attendees": [{"email": interviewer_email}, {"email": candidate_email}],
        # Ask Calendar to create a Meet conference
        "conferenceData": {
            "createRequest": {
                "requestId": f"req-{int(datetime.now().timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    created = (
        svc.events()
        .insert(
            calendarId=str(settings.GOOGLE_CALENDAR_ID),
            body=event_body,
            conferenceDataVersion=1,  # required to create Meet link
            sendUpdates="all",        # email invites
        )
        .execute()
    )

    # Meet link can be in either hangoutLink or conferenceData entryPoints
    meet_link = (
        created.get("hangoutLink")
        or created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
    )

    return {
        "eventId": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "meetLink": meet_link,
    }
