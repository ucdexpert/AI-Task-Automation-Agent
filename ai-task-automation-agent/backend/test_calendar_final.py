"""Test Google Calendar from JSON file"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# JSON file path
import os
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "agent493216-Be1814094638.json")

print("=" * 60)
print("Google Calendar Test")
print("=" * 60)

try:
    # Load credentials from JSON file
    with open(CREDENTIALS_FILE, 'r') as f:
        creds_dict = json.load(f)
    
    print(f"✅ Credentials loaded from file")
    print(f"   Service Account: {creds_dict.get('client_email')}")
    print(f"   Project: {creds_dict.get('project_id')}")
    
    # Create credentials object
    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, 
        scopes=scopes
    )
    print("✅ Credentials validated")
    
    # Build Calendar API client
    service = build('calendar', 'v3', credentials=credentials)
    print("✅ Calendar API client created")
    
    # Test: Get calendar info
    print("\n📅 Fetching calendar...")
    calendar = service.calendars().get(calendarId='primary').execute()
    print(f"✅ Connected to: {calendar.get('summary')}")
    print(f"   Timezone: {calendar.get('timeZone')}")
    
    # Test: List events
    print("\n📅 Upcoming events:")
    now = datetime.now(timezone.utc).isoformat()
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print("   ⚠️  No upcoming events")
        print("\n📌 Calendar share karna hai:")
        print("   1. Open https://calendar.google.com")
        print("   2. Settings → Settings for my calendars")
        print("   3. Select calendar → Share with specific people")
        print(f"   4. Add: {creds_dict.get('client_email')}")
        print("   5. Permission: 'Make changes to events'")
    else:
        print(f"   Found {len(events)} events:\n")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"   • {event.get('summary', 'No title')}")
            print(f"     {start}\n")
    
    print("\n✅ Google Calendar is working perfectly!")

except FileNotFoundError:
    print(f"❌ File not found: {CREDENTIALS_FILE}")
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ Error: {type(e).__name__}")
    if 'notFound' in error_msg or 'calendar' in error_msg.lower():
        print("   Calendar accessible nahi hai!")
        print("\n📌 Solution: Share your Google Calendar with:")
        print(f"   {creds_dict.get('client_email')}")
    else:
        print(f"   {error_msg}")
