
import logging
import optuna

from filters.financial import *
from filters.technical import *
from metrics import *
from data.service import *
from backtesting import *
from util.constant import INCLUDED_CODES


class OptunaCallBack(optuna.study.BaseStudy):
    def __init__(self) -> None:
        logging.basicConfig(filename="stat/opitmization.log", format='%(message)s', filemode='w')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        self.logger = logger
    
    def callback(self, study, trial):
        trial_data = {
            'trial_number': trial.number,
            'params': trial.params,
            'value': trial.value,
            'best': study.best_trial
        }
        self.logger.info(trial_data)


if __name__ == "__main__":
    optunaCallBack = OptunaCallBack()
    from_year = 2014
    to_year = 2024
    financial_data = data_service.get_financial_data(from_year, to_year, INCLUDED_CODES)

    from_date = "2017-01-01"
    to_date = "2024-04-25"

    daily_data = data_service.get_daily_data(from_date, to_date)
    daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
    daily_data = daily_data.astype({"liq": float, "close": float})
    
    financial_signal = FinancialSignal(financial_data)
    technical_signal = TechnicalSignal(daily_data)
    financial_factors = financial_signal.filter_median(["eps", "quick-ratio", "gm", "roe"])


    def objective(trial):
        rlb = trial.suggest_int(name="rlb", low=40, high=50, step = 5)
        rub = trial.suggest_int(name="rub", low=60, high=70, step = 5)
        technical_factors = technical_signal.filter_signal([("liquidity", 20, 1e6, 5e6), ("rsi", 60, rlb / 100, rub / 100)])

        signal_factors = merging([technical_factors, financial_factors], columns=["year", "quarter", "tickersymbol"])
        sorted_signal_factors = signal_factors.sort_values(by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]).groupby("date").head(3)
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        bt = Backtesting(portfolio, daily_data, 60)
        asset = bt.strategy(amt_each_stock=2e4)
        metrics = Metrics(asset)

        return metrics.expected_sharpe_portfolio()


    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100, callbacks=[OptunaCallBack()])