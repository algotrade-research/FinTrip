import os
import pandas as pd

from data.service import *
from util.visualization import *
from util.metric_func import *

class Metrics:
    def __init__(self, asset, index_data = None, index_window = 61):
        self.index_data = index_data
        self.index_window = index_window
        self.asset = asset.groupby(["start-date", "curr-date"])["unrealized-asset"].last(1).reset_index()

    def _init_index(self, apply_func, args=()):
        if self.index_data is not None:
            indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=self.index_window)
            return self.index_data["close"].rolling(window = indexer).apply(apply_func, args=args)

        return self.index_data
    
    def sharpe_index_df(self):
        sharpe_index_data = self._init_index(sharpe)
        rolling_sharpe_index_data = self.index_data.copy()
        rolling_sharpe_index_data["sharpe-ratio-index"] = sharpe_index_data
        rolling_sharpe_index_data = rolling_sharpe_index_data.dropna()

        return rolling_sharpe_index_data
    
    def sharpe_portfolio_df(self):
        sharpe_df = self.asset.groupby("start-date")["unrealized-asset"].apply(sharpe).reset_index().rename(columns={"unrealized-asset": "sharpe-ratio"}).rename(columns={"start-date": "date"})
        return sharpe_df
    
    def expected_sharpe(self):
        portfolio = self.sharpe_portfolio_df()
        index = self.sharpe_index_df()

        return index["sharpe-ratio-index"].mean(), portfolio["sharpe-ratio"].mean()
    
    def visualize_sharpe(self, path):
        portfolio = self.sharpe_portfolio_df()
        index = self.sharpe_index_df()
        merged = pd.merge(index, portfolio, on=["date"])
        visualize_with_index(merged["date"], 
                             merged["sharpe-ratio"], 
                             merged["sharpe-ratio-index"], 
                             title="Daily Sharpe Ratio",
                             x_label="date",
                             y_label="sharpe ratio",
                             path=path
                             )
        
        return merged[["date", "sharpe-ratio-index", "sharpe-ratio"]].copy()

    def mdd_index_df(self):
        mdd_index_data = self._init_index(mdd)
        rolling_mdd_index_data = self.index_data.copy()
        rolling_mdd_index_data["mdd-index"] = mdd_index_data
        rolling_mdd_index_data = rolling_mdd_index_data.dropna()

        return rolling_mdd_index_data

    def mdd_portfolio_df(self):
        mdds = self.asset.groupby("start-date")["unrealized-asset"].apply(mdd).reset_index().rename(columns={"unrealized-asset": "mdd"}).rename(columns={"start-date": "date"})
        mdds = mdds.dropna()

        return mdds
    
    def max_mdd(self):
        portfolio = self.mdd_portfolio_df()
        index = self.mdd_index_df()

        return index["mdd-index"].min(), portfolio["mdd"].mean()
    
    def pp_index_df(self, benchmark):
        pp_index_data = self._init_index(positive_percentage, args=(benchmark,))
        rolling_pp_index_data = self.index_data.copy()
        rolling_pp_index_data["pp-index"] = pp_index_data
        rolling_pp_index_data = rolling_pp_index_data.dropna()

        return rolling_pp_index_data
    
    def pp_portfolio_df(self, benchmark):
        pp = self.asset.groupby("start-date")["unrealized-asset"].apply(lambda x: positive_percentage(x, benchmark)).reset_index().rename(columns={"unrealized-asset": "pp"}).rename(columns={"start-date": "date"})
        
        return pp
    
    def pp(self, benchmark):
        portfolio = self.pp_portfolio_df(benchmark)
        index = self.pp_index_df(benchmark)
        i_positive = len(index[index["pp-index"] > 0]) / len(index)
        p_positive = len(portfolio[portfolio["pp"] > 0]) / len(portfolio)
        
        return 100 * i_positive, 100 * p_positive
    
    def ar_portfolio_df(self):
        ar = self.asset.groupby("start-date")["unrealized-asset"].apply(absolute_return).reset_index().rename(columns={"unrealized-asset": "ar"}).rename(columns={"start-date": "date"})
        
        return ar
    
    def ar_index_df(self):
        ar_index_data = self._init_index(absolute_return)
        rolling_ar_index_data = self.index_data.copy()
        rolling_ar_index_data["ar-index"] = ar_index_data
        rolling_ar_index_data = rolling_ar_index_data.dropna()

        return rolling_ar_index_data

    def ar(self):
        portfolio = self.ar_portfolio_df()
        index = self.ar_index_df()

        min_index =  index["ar-index"].min()
        max_index = index["ar-index"].max()
        mean_index = index["ar-index"].mean()
    
        min_portfolio =  portfolio["ar"].min()
        max_portfolio = portfolio["ar"].max()
        mean_portfolio = portfolio["ar"].mean()
        
        return min_index, max_index, mean_index, min_portfolio, max_portfolio, mean_portfolio

    def visualize_ar(self, path):
        portfolio = self.ar_portfolio_df()
        index = self.ar_index_df()
        merged = pd.merge(index, portfolio, on=["date"])
        visualize_with_index(merged["date"], 
                             merged["ar"], 
                             merged["ar-index"], 
                             title="Daily Absolute Return",
                             x_label="date",
                             y_label="accumulation return",
                             path=path
                             )
        
        return merged[["date", "ar-index", "ar"]].copy()
    
    def monthly_return_portfolio_df(self):
        monthly_return = self.asset.groupby("start-date")["unrealized-asset"].apply(expected_monthly_return).reset_index().rename(columns={"unrealized-asset": "monthly-return"}).rename(columns={"start-date": "date"})
        
        return monthly_return

    def monthly_return_index(self):
        monthly_return_index_data = self._init_index(expected_monthly_return)
        rolling_monthly_return_index_data = self.index_data.copy()
        rolling_monthly_return_index_data["monthly-return-index"] = monthly_return_index_data
        rolling_monthly_return_index_data = rolling_monthly_return_index_data.dropna()

        return rolling_monthly_return_index_data

    def monthly_return(self):
        portfolio = self.monthly_return_portfolio_df()
        index = self.monthly_return_index()

        return index["monthly-return-index"].mean(), portfolio["monthly-return"].mean()

    def no_stocks(self, portfolio, path):
        trading_dates = self.index_data["date"]
        count = portfolio.groupby("date").count().reset_index().rename(columns={"tickersymbol": "no-stocks"})
        merge = pd.merge(trading_dates, count, on=["date"], how="left")
        merge = merge.fillna(0)
        count = merge["no-stocks"].value_counts()
        count.plot(kind="bar", title="no stocks frequency", xlabel="number of stocks", ylabel="days").get_figure().savefig(path)

        return count

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), 'stat/asset')
    files = [os.path.splitext(file)[0] for file in os.listdir(path)]

    for key in files:
        assets = pd.read_csv(f"stat/asset/{key}.csv")
        assets["start-date"] = pd.to_datetime(assets["start-date"]).dt.date
        assets["curr-date"] = pd.to_datetime(assets["curr-date"]).dt.date
        assets = assets.sort_values(by=["start-date", "curr-date"])

        # get VNINDEX data
        from_date = assets["start-date"].iloc[0]
        to_date = assets["curr-date"].iloc[-1]
        index_data = data_service.get_index_data(from_date, to_date)
        index_data = index_data.astype({"open": float, "close": float})

        metrics = Metrics(asset=assets, index_data=index_data)

        # visualization
        sharpe_visualization = metrics.visualize_sharpe(path=f"stat/sharpe/{key}.png")
        ar_visualization = metrics.visualize_ar(path=f"stat/ar/{key}.png")
        
        # no stocks
        portfolio = pd.read_csv(f"stat/portfolio/{key}.csv")
        portfolio["date"] = pd.to_datetime(portfolio["date"]).dt.date
        no_stocks = metrics.no_stocks(portfolio, path=f"stat/no-stocks/{key}.png")

        # metrics
        esi, esp = metrics.expected_sharpe()
        mi, mp = metrics.max_mdd()
        ip, pp = metrics.pp(benchmark=0.05)
        ar_index_min, ar_index_max, ar_index_mean, ar_portfolio_min, ar_portfolio_max, ar_portfolio_mean = metrics.ar()
        monthly_return_index, monthly_return_portfolio = metrics.monthly_return()

        print(key)
        print("sharpe index", esi, "sharpe portfolio", esp)
        print("max mdd index", mi, "max mdd portfolio", mp)
        print("positive percentage index", ip, "positive percentage porfolio", pp)
        print("min, max, mean absolute retrun index", ar_index_min, ar_index_max, ar_index_mean)
        print("min, max, mean absolute retrun portfolio", ar_portfolio_min, ar_portfolio_max, ar_portfolio_mean)
        print("monthly return index", monthly_return_index, "monthly return portfolio", monthly_return_portfolio)