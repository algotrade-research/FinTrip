import pandas as pd
import pandas.testing as pd_testing

from filters.financial import *
import unittest


class TestFinancial(unittest.TestCase):
    def setUp(self) -> None:
        financial_data = pd.read_csv("mock/in-sample/financial_data.csv")
        self.financial_data = financial_data

    def test_eps(self):
        # target
        year = 2019
        quarter = 1
        firm = "FPT"
        val_4110 = 6136367720000.0000  # Owners Capital
        val_72 = 626304276321.0000  # Net Profit After Tax Attribute To Majority
        target = val_72 * 10000 / val_4110

        # function
        financial = FinancialSignal(self.financial_data)
        eps = financial.eps()
        eps_val = eps[
            (eps["year"] == year)
            & (eps["quarter"] == quarter)
            & (eps["tickersymbol"] == firm)
        ]

        self.assertEqual(eps_val.iloc[0]["eps"], target)

    def test_quick_ratio(self):
        # target
        year = 2019
        quarter = 1
        firm = "FPT"
        val_1100 = 2678204837715.0000  # Cash and Cash Equivalants
        val_1200 = 5727896026412.0000  # Short-term Investment
        val_1300 = 5872491479218.0000  # Current Accounts Receivable
        val_3100 = 12709176054673.0000  # Current Liabilities
        target = (val_1100 + val_1200 + val_1300) / val_3100

        # function
        financial = FinancialSignal(self.financial_data)
        quick_ratio = financial.quick_ratio()
        quick_ratio_val = quick_ratio[
            (quick_ratio["year"] == year)
            & (quick_ratio["quarter"] == quarter)
            & (quick_ratio["tickersymbol"] == firm)
        ]

        self.assertEqual(quick_ratio_val.iloc[0]["quick-ratio"], target)

    def test_gross_margin(self):
        # target
        year = 2019
        quarter = 1
        firm = "FPT"
        val_10 = 5672126363409.0000  # Gross Revenue
        val_30 = 2279330299668.0000  # Profit
        target = val_30 / val_10

        # function
        financial = FinancialSignal(self.financial_data)
        gross_margin = financial.gross_margin()

        gross_margin_val = gross_margin[
            (gross_margin["year"] == year)
            & (gross_margin["quarter"] == quarter)
            & (gross_margin["tickersymbol"] == firm)
        ]

        self.assertEqual(gross_margin_val.iloc[0]["gm"], target)

    def test_roe(self):
        # target
        year = 2019
        quarter = 1
        firm = "FPT"
        val_21 = 3387149316396.0000  # Cogs
        val_1400 = 1465488400196.0000  # Inventory
        target = val_21 / val_1400

        # function
        financial = FinancialSignal(self.financial_data)
        ti = financial.turnover_inventory()

        ti_val = ti[
            (ti["year"] == year)
            & (ti["quarter"] == quarter)
            & (ti["tickersymbol"] == firm)
        ]

        self.assertEqual(ti_val.iloc[0]["turnover-inv"], target)

    def test_get_signal(self):
        signals = ["eps", "gm", "turnover-inv", "roe", "quick-ratio"]
        financial = FinancialSignal(self.financial_data)

        for signal in signals:
            if signal == "eps":
                pd_testing.assert_frame_equal(
                    financial.eps(), financial.get_signal(signal)
                )

            elif signal == "gm":
                pd_testing.assert_frame_equal(
                    financial.gross_margin(), financial.get_signal(signal)
                )

            elif signal == "quick-ratio":
                pd_testing.assert_frame_equal(
                    financial.quick_ratio(), financial.get_signal(signal)
                )

            elif signal == "roe":
                pd_testing.assert_frame_equal(
                    financial.roe(), financial.get_signal(signal)
                )

            elif signal == "turnover-inv":
                pd_testing.assert_frame_equal(
                    financial.turnover_inventory(), financial.get_signal(signal)
                )

    def test_filter_median(self):
        # target
        year = 2019
        quarter = 1

        financial = FinancialSignal(self.financial_data)
        signals = ["eps", "gm", "turnover-inv", "roe", "quick-ratio"]

        signal_list = []
        for signal in signals:
            signal_list.append(signal)

            signal_df = []
            for item in signal_list:
                signal_df.append(financial.get_signal(item))

            merged = merging(signal_df, columns=["year", "quarter", "tickersymbol"])
            merged = merged[(merged["year"] == year) & (merged["quarter"] == quarter)]

            filtered = financial.filter_median(signal_list)
            filtered = filtered[
                (filtered["year"] == year) & (filtered["quarter"] == quarter)
            ]
            filtered = filtered[["year", "quarter", "tickersymbol"]]

            medians = {}
            for item in signal_list:
                median_val = merged[item].agg(["median"]).values[0]
                medians[item] = median_val

            for key in medians:
                merged = merged[merged[key] > medians[key]]

            merged = merged[["year", "quarter", "tickersymbol"]]
            pd_testing.assert_frame_equal(merged, filtered)


if __name__ == "__main__":
    unittest.main()
