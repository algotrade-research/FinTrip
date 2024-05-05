import pandas as pd
from visualization import *

if __name__ == "__main__":
    trading_dates = pd.read_csv("stat/trading_days.csv")
    keys = ["eps", "gm", "quick-ratio", "roe", "turnover-inv", "combine"]

    for key in keys:
        portfolio = pd.read_csv(f"stat/portfolio/{key}_portfolio.csv")
        count = portfolio.groupby("date").count().reset_index().rename(columns={"tickersymbol": "no-stocks"})
        merge = pd.merge(trading_dates, count, on=["date"], how="left")
        merge = merge.fillna(0)
        count = merge["no-stocks"].value_counts()
        print(key, count)
        count.plot(kind="bar").get_figure().savefig(f"stat/visualization/{key}.png")