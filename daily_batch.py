import pandas as pd
import openpyxl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from config.settings import CALENDAR_ID
from config.settings import KEY_FILEPATH
from config.settings import FILE_PATH
import config.constants as const
from common import convert_time

def send_event(service, calendar_id, event, event_type, event_id=None):
    if event_type == const.SYNC_FLG_NEW:
        return service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
    elif event_type == const.SYNC_FLG_UPDATE:
        return service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
    elif event_type == const.SYNC_FLG_DELETE:
        return service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
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
    
    target_idx = df[df[const.COL_SYNC_FLG].isin(
        [const.SYNC_FLG_NEW, const.SYNC_FLG_UPDATE, const.SYNC_FLG_DELETE]
    )].index

    for index in target_idx:
        try:
            row = df.loc[index]
            event_type = row[const.COL_SYNC_FLG]
            event_id = row.get(const.COL_EVENT_ID)
            if event_type in (const.SYNC_FLG_UPDATE, const.SYNC_FLG_DELETE) and not event_id:
                raise ValueError("event_id not found!")

            if event_type in (const.SYNC_FLG_NEW, const.SYNC_FLG_UPDATE):
                event = build_event(row)
                result = send_event(
                    service,
                    calendar_id,
                    event,
                    event_type,
                    event_id
                )
            elif event_type == const.SYNC_FLG_DELETE:
                send_event(
                    service,
                    calendar_id,
                    None,
                    event_type,
                    event_id
                )
                result = None

            if event_type == const.SYNC_FLG_NEW:
                df.loc[index, const.COL_EVENT_ID] = result["id"]
                df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_SYNCED
            elif event_type == const.SYNC_FLG_UPDATE:
                df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_SYNCED
            elif event_type == const.SYNC_FLG_DELETE:
                df.loc[index, const.COL_EVENT_ID] = ''
                df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_NONE
        except Exception as e:
            df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_ERROR
            print(f"index={index}, error={e}")



def main():
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILEPATH,
        scopes=const.SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)

    df = pd.read_excel(
        FILE_PATH,
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
    
    df.to_excel(FILE_PATH, index=False)
    print("正常終了")


if __name__ == "__main__":
    main()
