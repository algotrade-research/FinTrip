import pandas as pd

from util.utils import *

class TechnicalSignal():
    def __init__(self, data) -> None:
        self.data = data


    def liquidity(self, window, low, high):
        median_liq = self.data.groupby("tickersymbol").rolling(window, on="date")["liq"].agg(["median"]).shift(1).reset_index().rename(columns = {"median": "median-liq"})
        liq_data = pd.merge(self.data, median_liq, on=["date", "tickersymbol"])
        if high is not None and low is not None:
            liq_data = liq_data[(liq_data["median-liq"] >= low) & (liq_data["median-liq"] <= high)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        if high is None and low is not None:
            liq_data = liq_data[(liq_data["median-liq"] >= low)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        if high is not None and low is None:
            liq_data = liq_data[(liq_data["median-liq"] <= high)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        return None
    

    def ewm_rsi(self, window, low, high):
        def calculate_rsi(df, period):
            delta = df.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
            avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

            rs = avg_gain / avg_loss
            rsi = 1 - (1 / (1 + rs))
            return rsi

        rsi = self.data.groupby("tickersymbol")["close"]
        data = None
        for _, group in rsi:
            rsi_series = calculate_rsi(group, window)
            rsi_series = rsi_series.shift(1)
            data = rsi_series if data is None else pd.concat([data, rsi_series])

        rsi_data = self.data.copy()
        rsi_data["rsi"] = data.round(2)
        rsi_data = rsi_data.dropna()
        rsi_data = rsi_data[rsi_data["rsi"].between(low, high)]

        rsi_data = rsi_data[["year", "quarter", "date", "tickersymbol", "rsi"]].copy()
        return rsi_data
    

    def get_signal(self, signal):
        name, window, low, high = signal
        if name == "liquidity":
            return self.liquidity(window, low, high)
        
        if name == "rsi":
            return self.ewm_rsi(window, low, high)
    

    def filter_signal(self, signals):
        signal_data = []
        for signal in signals:
            signal_data.append(self.get_signal(signal))
        
        technical_factors = merging(signal_data, columns=["year", "quarter", "date", "tickersymbol"])
        return technical_factors
