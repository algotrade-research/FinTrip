import numpy as np
import pandas as pd
from config import *


def sharpe(asset, risk_free_rate):
    if len(asset) <= 1:
        return None

    daily_return = asset.iloc[1:].to_numpy() / asset.iloc[:-1].to_numpy() - 1

    annual_std = np.sqrt(252) * np.std(daily_return)
    if annual_std == 0:
        return None

    annual_return = 252 * np.mean(daily_return) - risk_free_rate
    sharpe = annual_return / annual_std
    return sharpe


def mdd(asset):
    df = pd.DataFrame(asset.values, columns=["unrealized-asset"])
    df["peak"] = df.apply(
        lambda row: df.loc[: row.name, "unrealized-asset"].max(), axis=1
    )
    df["drawdown"] = df["unrealized-asset"] / df["peak"] - 1

    mdd = df["drawdown"].min() * 100
    return mdd


def positive_percentage(asset, benchmark):
    ac_return = asset.iloc[:].to_numpy() / asset.iloc[0] - 1

    return 100 * len(ac_return[ac_return > benchmark]) / len(ac_return)


def absolute_return(asset):
    ar = asset.iloc[-1] / asset.iloc[0] - 1

    return 100 * ar


def expected_monthly_return(asset):
    df = pd.DataFrame(asset.values, columns=["unrealized-asset"])
    monthly_return = (
        df["unrealized-asset"]
        .rolling(window=20)
        .apply(lambda x: x.iloc[-1] / x.iloc[0] - 1)
    )
    return 100 * monthly_return.mean()
