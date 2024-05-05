from datetime import datetime

from data.service import *
from util.constant import INCLUDED_CODES
from filters.financial import *
from filters.technical import *
from backtesting import *
from metrics import *

if __name__ == "__main__":
    from_year = 2014
    to_year = 2024
    from_date = "2015-01-01"
    to_date = "2024-04-25"

    print("Fetching Data...")
    financial_data = data_service.get_financial_data(from_year, to_year, INCLUDED_CODES)

    daily_data = data_service.get_daily_data(from_date, to_date)
    daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
    daily_data = daily_data.astype({"liq": float, "close": float})

    index_data = data_service.get_index_data(from_date, to_date)
    index_data["date"] = pd.to_datetime(index_data["date"]).dt.date
    index_data = index_data.astype({"open": float, "close": float})
    
    financial_signal = FinancialSignal(financial_data)
    technical_signal = TechnicalSignal(daily_data)

    print("Calculating Technical Signal...")
    technical_factors  = technical_signal.filter_signal([("liquidity", 20, 1e6, 5e6), ("rsi", 60, 0.6, 0.7)])

    print("Calculating Financial Signal...")
    keys = ["eps", "quick-ratio", "gm", "roe", "turnover-inv", "combine"]
    in_sample_from_date = datetime.strptime("2017-01-01", "%Y-%m-%d").date()
    in_sample_to_date = datetime.strptime("2019-01-01", "%Y-%m-%d").date()
    in_sample_trading_days = index_data[index_data["date"].between(in_sample_from_date, in_sample_to_date)]["date"].to_csv("trading_days.csv")
    for key in keys:
        financial_factors = financial_signal.filter_median([key]) if key != "combine" else financial_signal.filter_median(["turnover-inv", "quick-ratio", "gm"])

        top = 3
        signal_factors = merging([technical_factors, financial_factors], columns=["year", "quarter", "tickersymbol"])
        sorted_signal_factors = signal_factors.sort_values(by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]).groupby("date").head(top)
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        in_sample_portfolios = portfolio[portfolio["date"].between(in_sample_from_date, in_sample_to_date)]
        in_sample_portfolios.to_csv(f"stat/portfolio/{key}_portfolio.csv", index=False)
        bt = Backtesting(in_sample_portfolios, daily_data, 60, 3)
        print("Backtesting...")
        assets = bt.strategy(amt_each_stock=2e4)
        assets.to_csv(f"stat/asset/{key}_asset.csv", index=False)
       