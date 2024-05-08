import pandas as pd
from datetime import datetime, timedelta

def merging(dfs: list[pd.DataFrame], columns) -> pd.DataFrame:
    merged_df = dfs[0]
    for i in range(1, len(dfs)):
        new_df = pd.merge(merged_df, dfs[i], on = columns, how='inner')
        merged_df = new_df.copy()

    return merged_df.dropna()

def get_date(from_date_str, to_date_str, forward_period, look_back):
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d")
    forward_delta =  timedelta(days = forward_period)
    look_back_delta = timedelta(days = look_back)
    
    start = from_date - look_back_delta
    end = to_date + forward_delta
    return start.date(), from_date.date(), to_date.date(), end.date()
