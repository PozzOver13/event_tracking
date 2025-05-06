import os
import datetime


from event_tracking.components.calendar import fetch_calendar_events, process_calendar_events
from event_tracking.config import RAW_DATA_DIR

if __name__ == "__main__":
    days=150
    today_date = datetime.datetime.now().strftime("%Y%m%d")

    events = fetch_calendar_events(days)
    events_df = process_calendar_events(events)

    file_name = f'my_calendar_db_{today_date}.parquet'
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    events_df.to_parquet(file_path)