import numpy as np
import pandas as pd
from data.service import *
from visualization import *

def sharpe(asset):
    if len(asset) <= 1:
        return None

    daily_return = asset.iloc[1:].to_numpy() / asset.iloc[:-1].to_numpy() - 1
    risk_free_rate = 0.03

    annual_std = np.sqrt(252) * np.std(daily_return)
    if annual_std == 0:
        return None

    annual_return = 252 * np.mean(daily_return) - risk_free_rate
    sharpe = annual_return / annual_std
    return sharpe

def mdd(asset):
    df = pd.DataFrame(asset.values, columns=["unrealized-asset"])
    df['peak'] = df.apply(lambda row: df.loc[:row.name, 'unrealized-asset'].max(), axis=1)
    df['drawdown'] = df['unrealized-asset']/df['peak'] - 1

    mdd = df['drawdown'].min() * 100
    return mdd

def positive_percentage(asset, benchmark):
    ac_return = asset.iloc[:].to_numpy() / asset.iloc[0] - 1

    return len(ac_return[ac_return > benchmark]) / len(ac_return)

def absolute_return(asset):
    ar = asset.iloc[-1] / asset.iloc[0] - 1

    return ar

class Metrics():
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
        
        return i_positive, p_positive
    
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

        return index["ar-index"].min(), index["ar-index"].max(), portfolio["ar"].min(), portfolio["ar"].max()
    
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
    
    def monthly_return_df(self):
        # monthly_return = 
        pass
    

if __name__ == "__main__":
    keys = ["eps", "gm", "quick-ratio", "roe", "turnover-inv", "combine"]
    for key in keys:
        assets = pd.read_csv(f"stat/asset/{key}_asset.csv")
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
        
        esi, esp = metrics.expected_sharpe()
        mi, mp = metrics.max_mdd()
        ip, pp = metrics.pp(benchmark=0.05)
        ar_index_min, ar_index_max, ar_portfolio_min, ar_portfolio_max = metrics.ar()

        print(key)
        print("sharpe index", esi, "sharpe portfolio", esp)
        print("max mdd index", mi, "max mdd index", mp)
        print("positive percentage index", ip, "positive percentage porfolio", pp)
        print("min - max absolute retrun index", ar_index_min, ar_index_max, "min - max absolute return portfolio", ar_portfolio_min, ar_portfolio_max)
