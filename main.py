import pandas as pd
import openpyxl

def main():
    file_path = "test.xlsx"
    df = pd.read_excel(file_path)
    # print(df.columns)
    df = pd.read_excel(
        file_path,
        usecols=[
            "id",
            "task_name",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "sync_flg"
        ]
    )
    # print("↓Excelファイル読込み内容↓")
    # print(df)

    # print("↓target_df↓")
    target_df = df[df["sync_flg"].isin(["new", "update"])]
    # print(target_df)
    # print(target_df["id"].tolist())

    mask = df["sync_flg"].isin(["new", "update"])
    print("maskの中身")
    print(mask)
    print()
    print("target_dfの中身")
    print(target_df)

    df.loc[mask, "sync_flg"] = "synced"

    df.to_excel(file_path, index=False)

    

if __name__ == "__main__":
    main()
