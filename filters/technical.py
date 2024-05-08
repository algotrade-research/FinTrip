import pandas as pd

from util.utils import *

class TechnicalSignal:
    def __init__(self, data) -> None:
        self.data = data


    def liquidity(self, window, low, high):
        median_liq = self.data.groupby("tickersymbol").rolling(window, on="date")["liq"].agg(["median"]).shift(1).reset_index().rename(columns = {"median": "median-liq"})
        liq_data = pd.merge(self.data, median_liq, on=["date", "tickersymbol"])
        if high is not None and low is not None:
            liq_data = liq_data[(liq_data["median-liq"] >= low) & (liq_data["median-liq"] <= high)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        elif high is None and low is not None:
            liq_data = liq_data[(liq_data["median-liq"] >= low)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        elif high is not None and low is None:
            liq_data = liq_data[(liq_data["median-liq"] <= high)]
            liq_data = liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
            return liq_data

        return liq_data[["year", "quarter", "date", "tickersymbol", "median-liq"]].copy()
    

    def ewm_rsi(self, window, low, high):
        def ewm(prices):
            ret = 0
            alpha = 1 - 1 / window
            multiplier = 1
            divider = 0
            for price in prices.iloc[::-1]:
                ret += price * multiplier
                divider += multiplier
                multiplier *= alpha
            
            return ret / divider
            
        def calculate_rsi(df):
            delta = df.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window).apply(ewm)
            avg_loss = loss.rolling(window).apply(ewm)
            rs = avg_gain / avg_loss
            rsi = 1 - (1 / (1 + rs))
            return rsi

        rsi = self.data.groupby("tickersymbol")["close"]
        data = None
        for _, group in rsi:
            rsi_series = calculate_rsi(group)
            rsi_series = rsi_series.shift(1)
            data = rsi_series if data is None else pd.concat([data, rsi_series])

        rsi_data = self.data.copy()
        rsi_data["rsi"] = data.round(2)
        rsi_data = rsi_data.dropna()

        if high is not None and low is not None:
            rsi_data = rsi_data[rsi_data["rsi"].between(low, high)]

        elif high is None and low is not None:
            rsi_data = rsi_data[rsi_data["rsi"] >= low]
        
        elif high is not None and low is None:
            rsi_data = rsi_data[rsi_data["rsi"] <= high]

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
