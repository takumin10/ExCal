from datetime import datetime
import pandas as pd
import config.constants as const
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config.settings import KEY_FILEPATH
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def convert_time(bf_time):
    if pd.isna(bf_time):
        raise ValueError("time is NaN")

    if isinstance(bf_time, datetime):
        return bf_time.time()

    if isinstance(bf_time, str):
        parts = bf_time.split(":")
        if len(parts) == 3:
            return datetime.strptime(bf_time, "%H:%M:%S").time()
        if len(parts) == 2:
            return datetime.strptime(bf_time, "%H:%M").time()

    return bf_time

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILEPATH,
        scopes=const.SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)
    return service

def load_excel(file_path, column_names):
    return pd.read_excel(
        file_path,
        dtype={const.COL_EVENT_ID: "string"},
        usecols=column_names
    )

def until_utc_z(end_dt_naive: datetime) -> str:
    end_dt_jst = end_dt_naive.replace(tzinfo=const.TZ)
    end_dt_utc = end_dt_jst.astimezone(timezone.utc)
    return end_dt_utc.strftime("%Y%m%dT%H%M%SZ")