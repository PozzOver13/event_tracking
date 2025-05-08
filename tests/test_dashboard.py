import os
import pandas as pd

from event_tracking.components.dashboard import get_contribution_plot, sidebar_display
from event_tracking.config import RAW_DATA_DIR

file_path = os.path.join(RAW_DATA_DIR, 'my_calendar_db_20250508.parquet')

def test_db_events():
    df = pd.read_parquet(file_path)

    df['year_only'] = df['start_time'].dt.year.astype(str)
    df['year_month'] = df['start_time'].dt.strftime('%Y-%m')
    df['year_month_week'] = df['start_time'].dt.strftime('%Y-%m-') + df['week_number'].astype(str).str.zfill(2)

    print("done")


def test_get_contribution_plot():
    df = pd.read_parquet(file_path)

    df['year_only'] = df['start_time'].dt.year.astype(str)
    df['year_month'] = df['start_time'].dt.strftime('%Y-%m')
    df['year_month_week'] = df['start_time'].dt.strftime('%Y-%m-') + df['week_number'].astype(str).str.zfill(2)

    fig = get_contribution_plot(df, view="monthly")

    print("done")

def test_sidebar_display():
    df = pd.read_parquet(file_path)

    df['year_only'] = df['start_time'].dt.year.astype(str)
    df['year_month'] = df['start_time'].dt.strftime('%Y-%m')
    df['year_month_week'] = df['start_time'].dt.strftime('%Y-%m-') + df['week_number'].astype(str).str.zfill(2)

    dict_sidebar = sidebar_display(df)
    selected_year = dict_sidebar["selected_year"]
    selected_calendars = dict_sidebar["selected_calendars"]
    selected_time_scale = dict_sidebar["selected_time_scale"]

    print("done")
