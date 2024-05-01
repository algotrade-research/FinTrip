import psycopg2
import pandas as pd

from data.query import *
from config.config import *


class DataService():
    def __init__(self) -> None:
        self.connection = psycopg2.connect(**db_params)
        
        
    def get_financial_data(self, from_year: str, to_year: str, included_code: list[str]) -> pd.DataFrame:
        cursor = self.connection.cursor()
        cursor.execute(financial_info_query, (from_year, str(to_year), tuple(included_code),))

        queries = [query for query in cursor]
        cursor.close()

        columns = ["year", "quarter", "tickersymbol", "value", 'code']
        return pd.DataFrame(queries, columns=columns)
    

    def get_daily_data(self, from_date: str, to_date: str) -> pd.DataFrame:
        cursor = self.connection.cursor()
        cursor.execute(daily_data_query, (from_date, to_date))

        queries = [query for query in cursor]
        cursor.close()

        columns = ["year", "quarter", "date", "tickersymbol", "close", "liq"]
        return pd.DataFrame(queries, columns=columns)


    def get_index_data(self, from_date: str, to_date: str) -> pd.DataFrame:
        cursor = self.connection.cursor()
        cursor.execute(index_query, (from_date, to_date))

        queries = [query for query in cursor]
        cursor.close()

        columns = ["date", "open", "close"]
        return pd.DataFrame(queries, columns=columns)
    
data_service = DataService()