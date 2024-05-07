import numpy as np
import pandas as pd
from datetime import datetime
from data.service import *


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

def positive_percentage(asset):
    ac_return = asset.iloc[:].to_numpy() / asset.iloc[0] - 1

    return len(ac_return[ac_return > 0]) / len(ac_return)

class Metrics():
    def __init__(self, asset, index_data = None):
        self.index_data = index_data
        self.asset = asset.groupby(["start-date", "curr-date"])["unrealized-asset"].last(1).reset_index()

    def _init_index(self, apply_func, window = 61):
        if self.index_data is not None:
            indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window)
            return self.index_data["close"].rolling(window = indexer).apply(apply_func)

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
    
    def pp_index_df(self):
        pp_index_data = self._init_index(positive_percentage)
        rolling_pp_index_data = self.index_data.copy()
        rolling_pp_index_data["pp-index"] = pp_index_data
        rolling_pp_index_data = rolling_pp_index_data.dropna()
        return rolling_pp_index_data
    
    def pp_portfolio_df(self):
        pp = self.asset.groupby("start-date")["unrealized-asset"].apply(positive_percentage).reset_index().rename(columns={"unrealized-asset": "pp"}).rename(columns={"start-date": "date"})
        return pp
    
    def monthly_return_df(self):
        # monthly_return = 
        pass
    
    def expected_sharpe_portfolio(self):
        sharpe_df = self.sharpe_portfolio_df()
        return sharpe_df["sharpe-ratio"].mean()
    
    def expected_sharpe_index(self):
        sharpe_index_df = self.sharpe_index_df()
        return sharpe_index_df["sharpe-ratio-index"].mean()
    
    def max_mdd_portfolio(self):
        mdd_df = self.mdd_portfolio_df()
        return mdd_df["mdd"].min()
    
    def max_mdd_index(self):
        mdd_df = self.mdd_index_df()
        return mdd_df["mdd-index"].min()
    
    def max_mdd(self):
        portfolio = self.mdd_portfolio_df()
        index = self.mdd_index_df()
        merge = pd.merge(index, portfolio, on=["date"])
        return merge["mdd-index"].min(), merge["mdd"].mean()

    def expected_sharpe(self):
        portfolio = self.sharpe_portfolio_df()
        index = self.sharpe_index_df()
        merge = pd.merge(index, portfolio, on=["date"])
        return merge["sharpe-ratio-index"].mean(), merge["sharpe-ratio"].mean()
    
    def expected_pp(self):
        portfolio = self.pp_portfolio_df()
        index = self.pp_index_df()
        merge = pd.merge(portfolio, index, on=["date"])
        rpp = merge["pp"].copy() - merge["pp-index"].copy()
        return rpp.mean()
    
    def expected_app(self):
        portfolio = self.pp_portfolio_df()
        return portfolio["pp"].mean()
    
    def no_app(self):
        porfolio = self.pp_portfolio_df()
        return len(porfolio[porfolio["pp"] > 0]) / len(porfolio)

    
if __name__ == "__main__":
    keys = ["eps", "gm", "quick-ratio", "roe", "turnover-inv", "combine"]

    from_date = datetime.strptime("2017-01-01", "%Y-%m-%d").date()
    to_date = datetime.strptime("2020-01-01", "%Y-%m-%d").date()

    index_data = data_service.get_index_data(from_date, to_date)
    index_data = index_data.astype({"open": float, "close": float})

    for key in keys:
        assets = pd.read_csv(f"stat/asset/{key}_asset.csv")
        assets["start-date"] = pd.to_datetime(assets["start-date"]).dt.date
        assets["curr-date"] = pd.to_datetime(assets["curr-date"]).dt.date
        metrics = Metrics(asset=assets, index_data=index_data)
        
        esi, esp = metrics.expected_sharpe()
        mi, mp = metrics.max_mdd()
        epp = metrics.expected_pp()
        eapp = metrics.expected_app()
        no_app = metrics.no_app()

        print(key)
        print("sharpe index", esi, "sharpe portfolio", esp)
        print("max mdd index", mi, "max mdd index", mp)
        print("eapp", eapp)
        print("epp", epp)
        print("no app", no_app)