from data.service import *

from util.constant import INCLUDED_CODES

if __name__ == "__main__":
    from_year = 2018
    to_year = 2019
    from_date = "2018-01-01"
    to_date = "2019-01-01"
    
    financial_data = data_service.get_financial_data(from_year, to_year, INCLUDED_CODES)
    financial_data.to_csv("mock/financial_data.csv", index=False)

    daily_data = data_service.get_daily_data(from_date, to_date)
    daily_data.to_csv("mock/daily_data.csv", index=False)

    index_data = data_service.get_index_data(from_date, to_date)
    index_data.to_csv("mock/index_data.csv", index=False)