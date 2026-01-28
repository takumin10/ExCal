import pandas as pd
import openpyxl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from config.settings import CALENDAR_ID
import config.constants as const
from common import convert_time

def send_event(service, calendar_id, event, mode, event_id=None):
    if mode == const.SYNC_FLG_NEW:
        return service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()

    if mode == const.SYNC_FLG_UPDATE:
        return service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()

    raise ValueError("invalid sync mode")

def build_event(row):
    start_time = convert_time(row[const.COL_START_TIME])
    end_time   = convert_time(row[const.COL_END_TIME])

    start_dt = datetime.combine(row[const.COL_START_DATE].date(), start_time)
    end_dt   = datetime.combine(row[const.COL_END_DATE].date(), end_time)

    return {
        'summary': row[const.COL_TASK_NAME],
        'location': '',
        'description': '',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': const.TIMEZONE
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': const.TIMEZONE
        }
    }

def sync_df(service, df, calendar_id):
    target_df = df[df[const.COL_SYNC_FLG].isin([const.SYNC_FLG_NEW, const.SYNC_FLG_UPDATE])]
    for index, row in target_df.iterrows():
        event = build_event(row)

        result = send_event(
            service,
            calendar_id,
            event,
            row[const.COL_SYNC_FLG],
            row.get(const.COL_EVENT_ID)
        )

        if row[const.COL_SYNC_FLG] == const.SYNC_FLG_NEW:
            df.loc[index, const.COL_EVENT_ID] = result[const.COL_ID]

        df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_SYNCED

def main():
    file_path = "test.xlsx"
    key_filepath = "./config/service_account.json"
    credentials = service_account.Credentials.from_service_account_file(
        key_filepath,
        scopes=const.SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)

    # df = pd.read_excel(file_path)
    df = pd.read_excel(
        file_path,
        dtype={const.COL_EVENT_ID: "string"},
        usecols=[
            const.COL_ID,
            const.COL_TASK_NAME,
            const.COL_START_DATE,
            const.COL_END_DATE,
            const.COL_START_TIME,
            const.COL_END_TIME,
            const.COL_SYNC_FLG,
            const.COL_EVENT_ID
        ]
    )

    sync_df(service, df, CALENDAR_ID)
    
    df.to_excel(file_path, index=False)
    print("正常終了")


if __name__ == "__main__":
    main()
