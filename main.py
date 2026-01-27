import pandas as pd
import openpyxl

def main():
    file_path = "test.xlsx"
    # df = pd.read_excel(file_path)
    df = pd.read_excel(
        file_path,
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
    update_df = target_df[target_df["sync_flg"] == "update"]

    for _, row in new_df.iterrows():
        task_name = row["task_name"]
        start_date = row["start_date"]
        end_date = row["end_date"]
        start_time = row["start_time"]
        end_time = row["end_time"]

    for _, row in update_df.iterrows():
        print(row)
        eventId = row["eventId"]
        task_name = row["task_name"]
        start_date = row["start_date"]
        end_date = row["end_date"]
        start_time = row["start_time"]
        end_time = row["end_time"]

    # df.loc[mask, "sync_flg"] = "synced"
    # df.to_excel(file_path, index=False)

    

if __name__ == "__main__":
    main()
