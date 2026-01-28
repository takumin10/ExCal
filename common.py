from datetime import datetime
import pandas as pd

def convert_time(t):
    if pd.isna(t):
        raise ValueError("time is NaN")

    if isinstance(t, datetime):
        return t.time()

    if isinstance(t, str):
        parts = t.split(":")
        if len(parts) == 3:
            return datetime.strptime(t, "%H:%M:%S").time()
        if len(parts) == 2:
            return datetime.strptime(t, "%H:%M").time()

    return t