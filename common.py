from datetime import datetime
import pandas as pd

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