from event_tracking.components.calendar import *


def test_get_google_calendar_credentials():
    creds = get_google_calendar_credentials()

    print("true")

def test_get_calendars_to_include():
    calendars_to_include = get_calendars_to_include()

    print(calendars_to_include)

def test_fetch_calendar():
    creds = get_google_calendar_credentials()
    service = build('calendar', 'v3', credentials=creds)
    calendars = fetch_all_calendars(service)

    print(f'Trovati {len(calendars)} calendari')

def test_fetch_calendar_events():
    events = fetch_calendar_events(5)

    print(f'Trovati {len(events)} eventi.')


def test_process_calendar_events():
    events = fetch_calendar_events(5)
    events_df = process_calendar_events(events)

    print(events_df)
