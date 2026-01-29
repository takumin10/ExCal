from datetime import datetime
from config.settings import CALENDAR_ID, FILE_PATH
import config.constants as const
from common import convert_time, get_calendar_service, load_excel

def send_event(service, calendar_id, event, event_type, event_id=None):
    if event_type == const.SYNC_STATUS_NEW:
        return service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
    elif event_type == const.SYNC_STATUS_UPDATE:
        return service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
    elif event_type == const.SYNC_STATUS_DELETE:
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

    repeat_type = row[const.COL_REPEAT_TYPE]//TODO: ここから繰り返し予定の必須項目を作る関数に渡す。repeat_typeとrowを渡す。

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
    
    target_idx = df[df[const.COL_SYNC_STATUS].isin(
        [const.SYNC_STATUS_NEW, const.SYNC_STATUS_UPDATE, const.SYNC_STATUS_DELETE]
    )].index

    for index in target_idx:
        try:
            row = df.loc[index]
            event_type = row[const.COL_SYNC_STATUS]
            event_id = row.get(const.COL_EVENT_ID)
            if event_type in (const.SYNC_STATUS_UPDATE, const.SYNC_STATUS_DELETE) and not event_id:
                raise ValueError("event_id not found!")

            if event_type in (const.SYNC_STATUS_NEW, const.SYNC_STATUS_UPDATE):
                event = build_event(row)
                result = send_event(
                    service,
                    calendar_id,
                    event,
                    event_type,
                    event_id
                )
            elif event_type == const.SYNC_STATUS_DELETE:
                send_event(
                    service,
                    calendar_id,
                    None,
                    event_type,
                    event_id
                )
                result = None

            if event_type == const.SYNC_STATUS_NEW:
                df.loc[index, const.COL_EVENT_ID] = result["id"]
                df.loc[index, const.COL_SYNC_STATUS] = const.SYNC_STATUS_SYNCED
            elif event_type == const.SYNC_STATUS_UPDATE:
                df.loc[index, const.COL_SYNC_STATUS] = const.SYNC_STATUS_SYNCED
            elif event_type == const.SYNC_STATUS_DELETE:
                df.loc[index, const.COL_EVENT_ID] = ''
                df.loc[index, const.COL_SYNC_STATUS] = const.SYNC_STATUS_NONE
        except Exception as e:
            df.loc[index, const.COL_SYNC_STATUS] = const.SYNC_STATUS_ERROR
            print(f"index={index}, error={e}")



def main():
    try:
        service = get_calendar_service()
        df = load_excel(FILE_PATH, const.TASK_COLUMN_NAMES)
        sync_df(service, df, CALENDAR_ID)
        df.to_excel(FILE_PATH, index=False)
        print("正常終了")
    except Exception as e:
        print(f"異常終了: {e}")
        raise

if __name__ == "__main__":
    main()
