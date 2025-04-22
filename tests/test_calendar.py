from event_tracking.components.calendar import fetch_calendar_events, get_google_calendar_credentials, \
    process_calendar_events


def test_get_google_calendar_credentials():
    creds = get_google_calendar_credentials()

    print("true")

def test_fetch_calendar_events():
    events = fetch_calendar_events(5)

    print(f'Trovati {len(events)} eventi.')


def test_process_calendar_events():
    events = fetch_calendar_events(5)
    events_df = process_calendar_events(events)

    print(events_df)
