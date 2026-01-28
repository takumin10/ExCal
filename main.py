import pandas as pd
import openpyxl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from config.settings import CALENDAR_ID
import config.constants as const
from common import convert_time

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
    target_df = df[df[const.COL_SYNC_FLG].isin([const.SYNC_FLG_NEW, const.SYNC_FLG_UPDATE])]
    new_df = target_df[target_df[const.COL_SYNC_FLG] == const.SYNC_FLG_NEW]
    update_df = target_df[target_df[const.COL_SYNC_FLG] == const.SYNC_FLG_UPDATE]

    print("### new ###")
    for index, row in new_df.iterrows():
        start_time = convert_time(row[const.COL_START_TIME])
        end_time = convert_time(row[const.COL_END_TIME])
        
        start_dt = datetime.combine(row[const.COL_START_DATE].date(), start_time)
        end_dt   = datetime.combine(row[const.COL_END_DATE].date(), end_time)

        event = {
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
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_id = event_result[const.COL_ID]
        df.loc[index, const.COL_EVENT_ID] = event_id
        df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_SYNCED
        print(event_result)


    print("### update ###")
    for index, row in update_df.iterrows():
        start_time = convert_time(row[const.COL_START_TIME])
        end_time = convert_time(row[const.COL_END_TIME])
        
        start_dt = datetime.combine(row[const.COL_START_DATE].date(), start_time)
        end_dt   = datetime.combine(row[const.COL_END_DATE].date(), end_time)

        event = {
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
        event_result = service.events().update(calendarId=CALENDAR_ID, eventId=row[const.COL_EVENT_ID], body=event).execute()
        df.loc[index, const.COL_SYNC_FLG] = const.SYNC_FLG_SYNCED
        print(event_result)
    
    df.to_excel(file_path, index=False)
    print("正常終了")


if __name__ == "__main__":
    main()
