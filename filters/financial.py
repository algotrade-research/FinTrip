import pandas as pd

from util.utils import *


class FinancialSignal:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def eps(self):
        owner_capital = (
            self.data[self.data["code"] == 4110]
            .copy()
            .rename(columns={"value": "outstanding_share"})
            .drop(columns=["code"])
        )
        earning = (
            self.data[self.data["code"] == 72]
            .copy()
            .rename(columns={"value": "earning"})
            .drop(columns=["code"])
        )

        owner_capital["outstanding_share"] = (
            owner_capital["outstanding_share"].copy() / 10000
        )

        eps = pd.merge(
            earning, owner_capital, on=["year", "quarter", "tickersymbol"]
        ).sort_values(by=["year", "quarter", "tickersymbol"])
        eps["eps"] = eps["earning"].copy() / eps["outstanding_share"].copy()
        eps = eps[["year", "quarter", "tickersymbol", "eps"]].dropna()
        return eps

    def quick_ratio(self):
        cash = (
            self.data[self.data["code"] == 1100]
            .copy()
            .rename(columns={"value": "cash"})
            .drop(columns=["code"])
        )
        investment = (
            self.data[self.data["code"] == 1200]
            .copy()
            .rename(columns={"value": "investment"})
            .drop(columns=["code"])
        )
        receivable = (
            self.data[self.data["code"] == 1300]
            .copy()
            .rename(columns={"value": "receivable"})
            .drop(columns=["code"])
        )
        liabilities = (
            self.data[self.data["code"] == 3100]
            .copy()
            .rename(columns={"value": "liabilities"})
            .drop(columns=["code"])
        )

        quick_ratio = merging(
            [cash, receivable, liabilities], columns=["year", "quarter", "tickersymbol"]
        )
        quick_ratio = pd.merge(
            quick_ratio, investment, on=["year", "quarter", "tickersymbol"], how="left"
        ).sort_values(by=["year", "quarter", "tickersymbol"])

        quick_ratio["investment"] = quick_ratio["investment"].fillna(0)
        quick_ratio["quick-ratio"] = (
            quick_ratio["cash"].copy()
            + quick_ratio["investment"].copy()
            + quick_ratio["receivable"].copy()
        ) / quick_ratio["liabilities"]

        quick_ratio = (
            quick_ratio[["year", "quarter", "tickersymbol", "quick-ratio"]]
            .dropna()
            .copy()
        )
        return quick_ratio

    def gross_margin(self):
        revenue = (
            self.data[self.data["code"] == 10]
            .copy()
            .rename(columns={"value": "revenue"})
            .drop(columns=["code"])
        )
        profit = (
            self.data[self.data["code"] == 30]
            .copy()
            .rename(columns={"value": "profit"})
            .drop(columns=["code"])
        )

        gross_margin = pd.merge(
            profit, revenue, on=["year", "quarter", "tickersymbol"]
        ).sort_values(by=["year", "quarter", "tickersymbol"])
        gross_margin["gm"] = (
            gross_margin["profit"].copy() / gross_margin["revenue"].copy()
        )

        gross_margin = gross_margin[["year", "quarter", "tickersymbol", "gm"]].dropna()
        return gross_margin

    def roe(self):
        profit_after_tax = (
            self.data[self.data["code"] == 70]
            .copy()
            .rename(columns={"value": "profit"})
            .drop(columns=["code"])
        )
        equity = (
            self.data[self.data["code"] == 4100]
            .copy()
            .rename(columns={"value": "equity"})
            .drop(columns=["code"])
        )

        roe = pd.merge(
            profit_after_tax, equity, on=["year", "quarter", "tickersymbol"]
        ).sort_values(by=["year", "quarter", "tickersymbol"])
        roe["roe"] = roe["profit"].copy() / roe["equity"].copy()
        roe = roe[["year", "quarter", "tickersymbol", "roe"]].dropna()
        return roe

    def turnover_inventory(self):
        cogs = (
            self.data[self.data["code"] == 21]
            .rename(columns={"value": "cogs"})
            .drop(columns=["code"])
        )
        inventory = (
            self.data[self.data["code"] == 1400]
            .rename(columns={"value": "inv"})
            .drop(columns=["code"])
        )

        turnover_inventory = pd.merge(
            cogs, inventory, on=["year", "quarter", "tickersymbol"]
        ).sort_values(by=["year", "quarter", "tickersymbol"])
        turnover_inventory["turnover-inv"] = (
            turnover_inventory["cogs"].copy() / turnover_inventory["inv"].copy()
        )
        turnover_inventory = turnover_inventory[
            ["year", "quarter", "tickersymbol", "turnover-inv"]
        ].dropna()
        return turnover_inventory

    def get_signal(self, signal):
        if signal == "eps":
            return self.eps()
        if signal == "quick-ratio":
            return self.quick_ratio()
        if signal == "gm":
            return self.gross_margin()
        if signal == "roe":
            return self.roe()
        if signal == "turnover-inv":
            return self.turnover_inventory()

    def filter_median(self, signals):
        signal_data = []
        for signal in signals:
            signal_data.append(self.get_signal(signal))

        financial_factors = merging(
            signal_data, columns=["year", "quarter", "tickersymbol"]
        )
        median_data = [financial_factors]
        for signal in signals:
            median_val = (
                financial_factors.groupby(["year", "quarter"])[f"{signal}"]
                .agg(["median"])
                .reset_index()
                .rename(columns={"median": f"{signal}_median"})
            )
            median_data.append(median_val)

        filtered = merging(median_data, columns=["year", "quarter"])
        for signal in signals:
            filtered = filtered[filtered[f"{signal}"] > filtered[f"{signal}_median"]]

        return filtered
