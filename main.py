from datetime import datetime

from data.service import *
from util.constant import INCLUDED_CODES
from filters.financial import *
from filters.technical import *
from backtesting import *
from metrics import *

if __name__ == "__main__":
    # date config
    start, from_date, to_date, end = get_date("2017-01-01", "2019-01-01", look_back=120, forward_period=90)

    print("Fetching Data...")
    # financial data
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
    technical_factors  = technical_signal.filter_signal([("liquidity", 20, 1e6, 5e6), ("rsi", 60, 0.6, 0.7)])

    print("Calculating Financial Signal...")
    keys = ["eps", "quick-ratio", "gm", "roe", "turnover-inv", "combine"]
    for key in keys:
        financial_factors = financial_signal.filter_median([key]) if key != "combine" else financial_signal.filter_median(["turnover-inv", "gm"])

        top = 3
        signal_factors = merging([technical_factors, financial_factors], columns=["year", "quarter", "tickersymbol"])
        sorted_signal_factors = signal_factors.sort_values(by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]).groupby("date").head(top)
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        in_sample_portfolios = portfolio[portfolio["date"].between(from_date, to_date)]
        in_sample_portfolios.to_csv(f"stat/portfolio/{key}_portfolio.csv", index=False)
        bt = Backtesting(in_sample_portfolios, daily_data, 60, top)
        print("Backtesting...")
        assets = bt.strategy(amt_each_stock=2e4)
        assets.to_csv(f"stat/asset/{key}_asset.csv", index=False)
        