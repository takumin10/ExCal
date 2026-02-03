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
    until = end_dt.strftime('%Y%m%dT%H%M%SZ')

    repeat_pattern = row[const.COL_REPEAT_PATTERN]

    freq = None
    INTERVAL = None
    BYDAY = None
    BYSETPOS = None

    if repeat_pattern == const.REPEAT_DAILY:
        freq=const.REPEAT_DAILY
        INTERVAL=row[const.COL_INTERVAL]
        BYDAY="MO,TU,WE,TH,FR"
    elif repeat_pattern == const.REPEAT_WEEKLY:
        freq=const.REPEAT_WEEKLY
        INTERVAL=row[const.COL_INTERVAL]
        BYDAY=row[const.COL_DAYOFWEEK]
    elif repeat_pattern == const.REPEAT_MONTHLY_DAY:
        freq=const.MONTHLY
        INTERVAL=row[const.COL_INTERVAL]
    elif repeat_pattern == const.REPEAT_MONTHLY_THE:
        freq=const.MONTHLY
        INTERVAL=row[const.COL_INTERVAL]
        BYDAY=row[const.COL_DAYOFWEEK]
        BYSETPOS=row[const.COL_WEEKOFMONTH]
    
    rule = {}
    if repeat_pattern != const.REPEAT_NONE:
        rule["FREQ"] = freq
        rule["INTERVAL"] = INTERVAL

        if repeat_pattern in (const.REPEAT_DAILY, const.REPEAT_WEEKLY, const.REPEAT_MONTHLY_THE):
            if 'BYDAY' in locals():
                rule["BYDAY"] = BYDAY

        if repeat_pattern == const.REPEAT_MONTHLY_THE:
            rule["BYSETPOS"] = BYSETPOS

        rule["UNTIL"] = until
    
    rrule = "RRULE:" + ";".join(f"{k}={v}" for k, v in rule.items())

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
    if repeat_pattern != const.REPEAT_NONE:
        event['recurrence'] = [rrule]
    return event

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
