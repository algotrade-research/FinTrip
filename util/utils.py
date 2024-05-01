import pandas as pd

def merging(dfs: list[pd.DataFrame], columns) -> pd.DataFrame:
    merged_df = dfs[0]
    for i in range(1, len(dfs)):
        new_df = pd.merge(merged_df, dfs[i], on = columns, how='inner')
        merged_df = new_df.copy()

    return merged_df.dropna()