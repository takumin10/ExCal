import pandas as pd
import openpyxl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from config.settings import CALENDAR_ID

def main():
    file_path = "test.xlsx"
    key_filepath = "./config/service_account.json"
    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(
        key_filepath,
        scopes=scopes
    )
    service = build('calendar', 'v3', credentials=credentials)

    # df = pd.read_excel(file_path)
    df = pd.read_excel(
        file_path,
        dtype={"eventId": "string"},
        usecols=[
            "id",
            "task_name",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "sync_flg",
            "eventId"
        ]
    )
    target_df = df[df["sync_flg"].isin(["new", "update"])]
    new_df = target_df[target_df["sync_flg"] == "new"]
    # update_df = target_df[target_df["sync_flg"] == "update"]

    for _, row in new_df.iterrows():
        # print(row)
        # task_name = row["task_name"]
        # start_date = row["start_date"]
        # end_date = row["end_date"]
        # start_time = row["start_time"]
        # end_time = row["end_time"]
        start_dt = datetime.combine(row["start_date"].date(), row["start_time"])
        end_dt   = datetime.combine(row["end_date"].date(), row["end_time"])

        event = {
            'summary': row["task_name"],
            'location': '',
            'description': '',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Tokyo'
            }
        }
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_id = event_result["id"]
        df.loc[_, "eventId"] = event_id
        df.loc[_, "sync_flg"] = "synced"

    df.to_excel(file_path, index=False)
    print("正常終了")

    # for _, row in update_df.iterrows():
    #     print(row)
    #     eventId = row["eventId"]
    #     task_name = row["task_name"]
    #     start_date = row["start_date"]
    #     end_date = row["end_date"]
    #     start_time = row["start_time"]
    #     end_time = row["end_time"]


if __name__ == "__main__":
    main()
