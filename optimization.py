import logging
import optuna
from optuna.samplers import RandomSampler

from filters.financial import *
from filters.technical import *
from metrics import *
from data.service import *
from backtesting.backtesting import *
from util.constant import INCLUDED_CODES


class OptunaCallBack:
    def __init__(self) -> None:
        logging.basicConfig(
            filename="stat/optimization.log.csv", format="%(message)s", filemode="w"
        )
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        self.logger.info(f"number,llb,lub,value")

    def __call__(
        self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial
    ) -> None:
        llb = trial.params["llb"]
        lub = llb + trial.params["delta"]
        self.logger.info(f"{trial.number},{llb},{lub},{trial.value}")


if __name__ == "__main__":
    start, from_date, to_date, end = get_date(
        optimization_params["from_date"],
        optimization_params["to_date"],
        look_back=120,
        forward_period=90,
    )

    print("Fetching Data...")
    # financial_data = data_service.get_financial_data(start.year, to_date.year, INCLUDED_CODES)
    financial_data = data_service.get_financial_data(
        start.year, to_date.year, INCLUDED_CODES
    )

    # daily_data = data_service.get_daily_data(start, end)
    daily_data = data_service.get_daily_data(start, end)
    daily_data["date"] = pd.to_datetime(daily_data["date"]).dt.date
    daily_data = daily_data.astype({"liq": float, "close": float})

    financial_signal = FinancialSignal(financial_data)
    technical_signal = TechnicalSignal(daily_data)

    print("Calculating Technical Signal...")
    technical_factors = technical_signal.filter_signal(
        [
            ("liquidity", 20, None, None),
            ("rsi", 60, optimization_params["rsi_lb"], optimization_params["rsi_ub"]),
        ]
    )
    print("Calculating Financial Signal...")
    financial_factors = financial_signal.filter_median(
        optimization_params["combination"]
    )
    print(f"Number of trails: {optimization_params['no_trials']}")

    def objective(trial):
        llb = trial.suggest_int(
            name="llb",
            low=optimization_params["llb_low"],
            high=optimization_params["llb_high"],
            step=optimization_params["step"],
        )
        delta_high = trial.suggest_int(
            name="delta",
            low=optimization_params["delta_low"],
            high=optimization_params["delta_high"],
            step=optimization_params["step"],
        )
        filtered_technical_factors = technical_factors[
            technical_factors["median-liq"].between(llb, llb + delta_high)
        ]

        signal_factors = merging(
            [filtered_technical_factors, financial_factors],
            columns=["year", "quarter", "tickersymbol"],
        )
        sorted_signal_factors = (
            signal_factors.sort_values(
                by=["date", "rsi", "tickersymbol"], ascending=[True, False, True]
            )
            .groupby("date")
            .head(3)
        )
        portfolio = sorted_signal_factors[["date", "tickersymbol"]].copy()

        bt = Backtesting(portfolio, daily_data, 60, 3)
        asset = bt.strategy(amt_each_stock=2e4)
        metrics = Metrics(asset)
        sharpe = metrics.sharpe_portfolio_df()

        return sharpe["sharpe-ratio"].mean()

    optunaCallBack = OptunaCallBack()
    study = optuna.create_study(sampler=RandomSampler(seed=2024), direction="maximize")
    study.optimize(
        objective, n_trials=optimization_params["no_trials"], callbacks=[optunaCallBack]
    )
