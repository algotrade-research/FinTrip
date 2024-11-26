import argparse
from data.service import *

from util.constant import INCLUDED_CODES
from util.utils import get_date

if __name__ == "__main__":
    parser = argparse.ArgumentParser("mock generator")
    parser.add_argument("mode", help="backtesting or validation")
    args = parser.parse_args()

    start, from_date, to_date, end = (
        get_date(
            optimization_params["os_from_date"],
            optimization_params["os_to_date"],
            forward_period=90,
            look_back=120,
        )
        if args.mode == "validation"
        else get_date(
            backtesting_config["from_date"],
            backtesting_config["to_date"],
            forward_period=90,
            look_back=120,
        )
    )

    financial_path = (
        "mock/out-sample/financial_data.csv"
        if args.mode == "validation"
        else "mock/in-sample/financial_data.csv"
    )
    daily_path = (
        "mock/out-sample/daily_data.csv"
        if args.mode == "validation"
        else "mock/in-sample/daily_data.csv"
    )
    index_path = (
        "mock/out-sample/index_data.csv"
        if args.mode == "validation"
        else "mock/in-sample/index_data.csv"
    )

    print("Financial Data...")
    financial_data = data_service.get_financial_data(
        start.year, to_date.year, INCLUDED_CODES
    )
    financial_data.to_csv(financial_path, index=False)

    print("Daily Data...")
    daily_data = data_service.get_daily_data(start, end)
    daily_data.to_csv(daily_path, index=False)

    print("Index Data...")
    index_data = data_service.get_index_data(from_date, end)
    index_data.to_csv(index_path, index=False)
