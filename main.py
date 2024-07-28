from data.service import *
from util.constant import INCLUDED_CODES
from util.utils import *
from filters.financial import *
from filters.technical import *
from backtesting.backtesting import *
from metrics import *
from config import *

if __name__ == "__main__":
    # date config
    start, from_date, to_date, end = get_date(backtesting_config["from_date"], 
                                              backtesting_config["to_date"], 
                                              forward_period=90,
                                              look_back=120
                                              )

    print("Fetching Data...")
    # financial data
    # financial_data = data_service.get_financial_data(start.year, to_date.year, INCLUDED_CODES)
    financial_data = data_service.get_financial_data(start.year, to_date.year, INCLUDED_CODES, is_file=True, is_backtesting=True)


    # price data
    # daily_data = data_service.get_daily_data(start, end)
    daily_data = data_service.get_daily_data(start, end, is_file=True, is_backtesting=True)
    daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
    daily_data = daily_data.astype({"liq": float, "close": float})

    # VNINDEX data
    index_data = data_service.get_index_data(from_date, end)
    index_data["date"] = pd.to_datetime(index_data["date"]).dt.date
    index_data = index_data.astype({"open": float, "close": float})
    
    financial_signal = FinancialSignal(financial_data)
    technical_signal = TechnicalSignal(daily_data)

    print("Calculating Technical Signal...")
    technical_factors  = technical_signal.filter_signal([
        ("liquidity", backtesting_config["liquidity_look_back"], backtesting_config["liquidity_lb"], backtesting_config["liquidity_ub"]), 
        ("rsi", backtesting_config["rsi_look_back"], backtesting_config["rsi_lb"], backtesting_config["rsi_ub"])
    ])

    print("Calculating Financial Signal...")
    keys = ["eps", "quick-ratio", "gm", "roe", "turnover-inv", "combine"]
    for key in keys:
        if key == "combine" and backtesting_config["combination"] == []:
            continue

        financial_factors = financial_signal.filter_median([key]) if key != "combine" else financial_signal.filter_median(backtesting_config["combination"])

        top = backtesting_config["no_stock"]
        signal_factors = merging([technical_factors, financial_factors], columns=["year", "quarter", "tickersymbol"])
        sorted_signal_factors = signal_factors.sort_values(by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]).groupby("date").head(top)
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        in_sample_portfolios = portfolio[portfolio["date"].between(from_date, to_date)]
        in_sample_portfolios.to_csv(f"stat/in-sample/portfolio/{key}.csv", index=False)
        bt = Backtesting(in_sample_portfolios, daily_data, 60, top)
        print("Backtesting...")
        assets = bt.strategy(amt_each_stock=2e4)
        assets.to_csv(f"stat/in-sample/asset/{key}.csv", index=False)
        