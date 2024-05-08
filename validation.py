import pandas as pd

from backtesting import *
from util.utils import *
from data.service import *
from filters.financial import *
from filters.technical import *
from util.constant import INCLUDED_CODES


if __name__ == "__main__":
    optimized = pd.read_csv("stat/optimization.log.csv")
    distinct = optimized.groupby(["llb", "lub"]).head(1).reset_index()
    distinct = distinct.nlargest(5, columns=["value"])

    start, from_date, to_date, end = get_date("2019-01-01", "2022-01-01", look_back=120, forward_period=90)
    print("Fetching Data...")
    financial_data = data_service.get_financial_data(start.year, to_date.year, INCLUDED_CODES)

    # price data
    daily_data = data_service.get_daily_data(start, end)
    daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
    daily_data = daily_data.astype({"liq": float, "close": float})

    # VNINDEX data
    index_data = data_service.get_index_data(from_date, end)
    index_data["date"] = pd.to_datetime(index_data["date"]).dt.date
    index_data = index_data.astype({"open": float, "close": float})
    
    financial_signal = FinancialSignal(financial_data)
    technical_signal = TechnicalSignal(daily_data)

    print("Calculating Technical Signal...")
    technical_factors = technical_signal.filter_signal([("liquidity", 20, None, None), ("rsi", 60, 0.6, 0.7)])
    financial_factors = financial_signal.filter_median(["turnover-inv", "gm"])

    for _, row in distinct.iterrows():
        top = 3
        llb = row["llb"]
        lub = row["lub"]

        filtered_technical_factors = technical_factors[technical_factors["median-liq"].between(llb, lub)]
        signal_factors = merging([technical_factors, financial_factors], columns=["year", "quarter", "tickersymbol"])
        sorted_signal_factors = signal_factors.sort_values(by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]).groupby("date").head(top)
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        in_sample_portfolios = portfolio[portfolio["date"].between(from_date, to_date)]
        in_sample_portfolios.to_csv(f"stat/portfolio/{llb}_{lub}.csv", index=False)
        bt = Backtesting(in_sample_portfolios, daily_data, 60, top)
        print("Backtesting...")
        assets = bt.strategy(amt_each_stock=2e4)
        assets.to_csv(f"stat/asset/{llb}_{lub}.csv", index=False)
