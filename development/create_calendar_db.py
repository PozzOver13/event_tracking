import os

from event_tracking.components.calendar import fetch_calendar_events, process_calendar_events
from event_tracking.config import RAW_DATA_DIR

if __name__ == "__main__":
    days=90
    events = fetch_calendar_events(days)
    events_df = process_calendar_events(events)

    file_path = os.path.join(RAW_DATA_DIR, 'my_calendar_db.parquet')
    events_df.to_parquet(file_path)