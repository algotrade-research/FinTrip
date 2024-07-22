from datetime import datetime
import pandas as pd
import pandas.testing as pd_testing
import unittest

from filters.technical import *

class TestTechnical(unittest.TestCase):
    def setUp(self) -> None:
        technical_data = pd.read_csv("mock/daily_data.csv")
        technical_data["date"] = pd.to_datetime(technical_data["date"]).dt.date
        self.technical_data = technical_data


    def test_liquidity(self):
        # target
        firm = "FPT"
        test_day = datetime.strptime("2018-12-28", "%Y-%m-%d").date()
        daily_data = self.technical_data[(self.technical_data["tickersymbol"] == firm) & (self.technical_data["date"] < test_day)].iloc[-20:]
        meadian_target = daily_data["liq"].median()

        technical = TechnicalSignal(self.technical_data)
        liquidity = technical.liquidity(window=20, low=1e6, high=None)
        liquidity = liquidity[(liquidity["tickersymbol"] == firm) & (liquidity["date"] == test_day)]
        
        self.assertEqual(meadian_target, liquidity["median-liq"].iloc[0])


    def test_ewm_rsi(self):
        window = 20
        firm = "FPT"
        test_day = datetime.strptime("2018-12-28", "%Y-%m-%d").date()
        daily_data = self.technical_data[(self.technical_data["tickersymbol"] == firm) & (self.technical_data["date"] < test_day)].iloc[-window - 1:]
        daily_data["diff"]  = daily_data["close"].diff()
        daily_data["gain"] = daily_data.where(daily_data["diff"] > 0 , 0)["diff"]
        daily_data["loss"] = daily_data.where(daily_data["diff"] < 0, 0)["diff"]
        daily_data = daily_data.reindex(daily_data.index[::-1])
        daily_data = daily_data.iloc[:-1]

        avg_gain = 0
        avg_loss = 0
        alpha = 1 - 1 / window
        mulitplier = 1
        divider = 0

        for _, row in daily_data.iterrows():
            avg_gain += row["gain"] * mulitplier
            avg_loss += row["loss"] * mulitplier
            divider += mulitplier
            mulitplier *= alpha
        
        avg_gain /= divider
        avg_loss /= divider
        rsi_target = 1 - 1 / (1 + avg_gain / abs(avg_loss))


        technical = TechnicalSignal(self.technical_data)
        rsi = technical.ewm_rsi(window, None, None)
        rsi = rsi[(rsi["tickersymbol"] == firm) & (rsi["date"] == test_day)]
        self.assertEqual(round(rsi_target, 2), rsi.iloc[0]["rsi"])


    def test_get_signal(self):
        signals = [("liquidity", 20, None, None), ("rsi", 20, None, None)]
        technical = TechnicalSignal(self.technical_data)

        for signal in signals:
            sig_type = signal[0]
            if sig_type == "liquidity":
                pd_testing.assert_frame_equal(technical.liquidity(20, None, None), technical.get_signal(signal))

            elif sig_type == "rsi":
                pd_testing.assert_frame_equal(technical.ewm_rsi(20, None , None), technical.get_signal(signal))


    def test_filter_signal(self):
        technical = TechnicalSignal(self.technical_data)
        liquidity = technical.liquidity(20, 1e6, 5e6)
        rsi = technical.ewm_rsi(20, 0.6, 0.7)
        merged = merging([liquidity, rsi], columns=["year", "quarter", "date", "tickersymbol"])
        
        filtered = technical.filter_signal(signals=[("liquidity", 20, 1e6, 5e6), ("rsi", 20, 0.6, 0.7)])
        pd_testing.assert_frame_equal(merged, filtered)

    
if __name__ == "__main__":
    unittest.main()