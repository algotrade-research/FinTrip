from datetime import datetime
import pandas as pd
import unittest

from backtesting import *

class TestBacktesting(unittest.TestCase):
    def setUp(self):
        daily_data = pd.read_csv("mock/daily_data.csv")
        daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
        self.daily_data = daily_data
    
    def test_price(self):
        period = 10
        no_firms = 3
        portfolio = self.daily_data.groupby("date").head(no_firms).reset_index()
        end_date = datetime.strptime("2018-06-01", "%Y-%m-%d").date()
        portfolio = portfolio[portfolio["date"] <= end_date]
        portfolio = portfolio[["date", "tickersymbol"]]

        bt = Backtesting(portfolio, self.daily_data, period=period, no_firms=no_firms)
        prices = bt.price()

        tracking = {}
        curr_day = None
        for _, row in prices.iterrows():
            if curr_day != row["date"] and row["buy"]:
                curr_day = row["date"]
                tracking[curr_day] = {}
            
            if row["buy"]:
                tracking[curr_day][row["tickersymbol"]] = 0
            else:
                is_used = False
                for date in tracking:
                    for firm in tracking[date]:
                        if firm == row["tickersymbol"] and tracking[date][firm] < period:
                            tracking[date][firm] += 1
                            is_used = True

                self.assertEqual(is_used, True)
            
        for date in tracking:
            for firm in tracking[date]:
                self.assertEqual(tracking[date][firm], period)

        self.assertEqual(len(portfolio["date"].unique()), len(prices[prices["buy"]]["date"].unique()))
            

    def test_strategy(self):
        period = 10
        no_firms = 3
        daily_data = self.daily_data[self.daily_data["tickersymbol"] != "SPX"]
        portfolio = daily_data.groupby("date").head(no_firms).reset_index()
        end_date = datetime.strptime("2018-06-01", "%Y-%m-%d").date()
        portfolio = portfolio[portfolio["date"] <= end_date]
        portfolio = portfolio[["date", "tickersymbol"]]

        bt = Backtesting(portfolio, self.daily_data, period=period, no_firms=no_firms)
        assets = bt.strategy(amt_each_stock=2e4)

        holding_days = assets.groupby("start-date")["tickersymbol"].count().reset_index()
        dates = []
        for _, row in holding_days.iterrows():
            self.assertEqual(row["tickersymbol"], (period + 1) * no_firms)
            dates.append(row["start-date"])
        
        self.assertEqual(len(dates), len(portfolio["date"].unique().tolist()))
            