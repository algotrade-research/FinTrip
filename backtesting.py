import pandas as pd
import numpy as np

class Backtesting():
    def __init__(self, portfolio, daily_data, period, no_firms, buy_fee = 0.0015, sell_fee = 0.0025):
        self.portfolio = portfolio
        self.daily_data = daily_data
        self.period = period
        self.no_firms = no_firms
        self.buy_fee = buy_fee
        self.sell_fee = sell_fee


    def _init_data(self):
        self.end = []
        self.assets = []
        self.inv = {}
        self.unrealized_assets = {}


    def _update_asset(self, tickersymbol, price, updating_date):
        for d in self.inv:
            for index, firm in enumerate(self.inv[d]):
                if firm["tickersymbol"] != tickersymbol:
                    continue

                unrealized_pnl = firm["amt"] * (price - firm["current"])
                if firm["counter"] == 0:
                    realized_pnl = firm["amt"] * price
                    self.unrealized_assets[d] += unrealized_pnl - self.sell_fee * realized_pnl
                    self.end.append({"date": d, "index": index})
                    self.assets.append([d, updating_date, tickersymbol, firm["amt"], price, self.unrealized_assets[d]])
                    continue

                if firm["counter"] > 0:
                    firm["counter"] -= 1
                    self.unrealized_assets[d] += unrealized_pnl
                    firm["current"] = price

                    self.assets.append([d, updating_date, tickersymbol, firm["amt"], price, self.unrealized_assets[d]])


    def _clear_inv(self):
        if len(self.end) <= 0:
            return self.inv, self.end

        for firm in self.end:
            date_inv = self.inv[firm["date"]]
            new_inv = [date_inv[index] for index in range(len(date_inv)) if index != firm["index"]]
            self.inv[firm["date"]] = new_inv

        self.end = []
        return self.inv, self.end


    def _buy(self, amt_each_stock, buying_date, tickersymbol, price):
        no_stock = int (amt_each_stock / ((1 + self.buy_fee) * price * 100))

        if no_stock >= 1:
            no_stock *= 100
            self.unrealized_assets[buying_date] -= self.buy_fee * no_stock * price
            self.assets.append([buying_date, buying_date, tickersymbol, no_stock, price, self.unrealized_assets[buying_date]])

            self.inv[buying_date].append({"tickersymbol": tickersymbol, "start": price, "current": price, "amt": no_stock, "counter": self.period})


    def price(self):
        portfolio = self.portfolio.copy()
        prices = self.daily_data[["date", "tickersymbol", "close"]].copy()

        portfolio["holding-period"] = [self.period] * len(portfolio)
        prices = pd.merge(portfolio, prices, on=["date", "tickersymbol"], how="right").replace({np.nan: None})

        data = []
        count = {}
        date, tickersymbol, holding_period, close = zip(*prices.values)
        for i in range(len(date)):
            if tickersymbol[i] in count:
                count[tickersymbol[i]] -= 1
                data.append([date[i], tickersymbol[i], close[i], False])

                if count[tickersymbol[i]] == 0:
                    del count[tickersymbol[i]]

            if not (holding_period[i] is None):
                data.append([date[i], tickersymbol[i], close[i], True])
                count[tickersymbol[i]] = holding_period[i]

        return pd.DataFrame(data, columns=[ "date", "tickersymbol", "close", "buy"])


    def strategy(self, amt_each_stock):
        self._init_data()
        prices = self.price()
        prices.to_csv("prices.csv", index=False)

        date, tickersymbol, close, buy = zip(*prices.values)

        current_date = date[0]
        self.unrealized_assets[date[0]] = amt_each_stock * self.no_firms
        self.inv[date[0]] = []

        for i in range(len(date)):
            if current_date != date[i]:
                current_date = date[i]
                self.unrealized_assets[date[i]] = amt_each_stock * self.no_firms
                self.inv[date[i]] = []

            self.inv, self.end = self._clear_inv()

            if buy[i]:
                self._buy(amt_each_stock, date[i], tickersymbol[i], close[i])
                continue

            self._update_asset(tickersymbol[i], close[i], date[i])

        df = pd.DataFrame(self.assets, columns = ["start-date", "curr-date", "tickersymbol", "amt", "close", "unrealized-asset"])
        return df