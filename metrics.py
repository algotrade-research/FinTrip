import numpy as np
import pandas as pd


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


def holding_period_return(self):
    return 100 * (self.asset.iloc[-1] / self.asset.iloc[0] - 1)


def mdd(asset):
    df = pd.DataFrame(asset.values, columns=["unrealized-asset"])
    df['peak'] = df.apply(lambda row: df.loc[:row.name, 'unrealized-asset'].max(), axis=1)
    df['drawdown'] = df['unrealized-asset']/df['peak'] - 1

    mdd = df['drawdown'].min() * 100
    return mdd


def sortino(self):
    if len(self.asset) <= 1:
        return None

    daily_return = self.asset.iloc[1:].to_numpy() / self.asset.iloc[:-1].to_numpy() - 1
    mar = 0.07

    annual_std = np.sqrt(252) * np.std(daily_return[daily_return < 0])
    if annual_std == 0:
        return None

    annual_return = 252 * np.mean(daily_return) - mar
    sortino = annual_return / annual_std
    return sortino


def information_ratio(self):
    data = pd.merge(self.asset, self.index_asset, left_on=["curr-date"], right_on=["date"], how='inner')

    daily_return = data["unrealized-asset"].iloc[1:].to_numpy() / data["unrealized-asset"].iloc[:-1].to_numpy() - 1
    daily_benchmark_return = data["close"].iloc[1:].to_numpy() / data["close"].iloc[:-1].to_numpy() - 1
    diff = daily_return - daily_benchmark_return

    exess_return = daily_return.mean() - daily_benchmark_return.mean()
    tracking_err = np.std(diff)
    if tracking_err == 0:
        return None

    annual_ir = np.sqrt(252) * exess_return / tracking_err
    return annual_ir


class Metrics():
    def __init__(self, asset, index_asset):
        self.asset = asset
        self.index_data = index_asset

        self.last_date_assets = asset.groupby(["start-date", "curr-date"])["unrealized-asset"].last(1).reset_index()

    def sharpe_df(self):
        sharpe_df = self.last_date_assets.groupby("start-date")["unrealized-asset"].apply(self.sharpe).reset_index().rename(columns={"unrealized-asset": "sharpe-ratio"})
        return sharpe_df