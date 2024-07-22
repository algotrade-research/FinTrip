# Introduction
This project recommends 3 stocks daily in the Vietnam market by utilizing fundamental signals and technical signals calculated from financial statement and daily price data respectively.

# Feature
- [x] Generate Mock Data
- [x] Validate Test Case: Financial, Technical and Backtesting
- [x] Optimize hyperparameters
- [x] Evaluate backtesting and optimization
- [ ] Paper trade

# Data explaination
There are two types of data which are the financial statement and daily trading data. For the calculation, the data is collected from:
- start date: the beginning date of daily data includeing the look back data for the signal calculation
- end date: the end date of daily data including the last date for the return calculation
# Installation
- Requirement: pip, venv
- Create and source new virtual environment in the current working directory with command
```
python3 -m virtualenv venv
source .venv/bin/activate
```
- Install the dependencies by:
```
pip install -r requirements.txt
```
# Getting started
## Database Environment
- Create ```.env``` file and enter your data source configuration with the format
```
HOST=<host or ip>
PORT=<port>
DATABASE=<database name>
USER=<username>
PASSWORD=<password>
```
- source the .env file by the command:
```
source .env
```
## Data initiation
- To create the daily asset data with backtesting parameter run the ```main.py``` file
```
python main.py
```
- The daily asset data will be stored in folder ```stat/asset```. 
- Paramters are stored in ```parameter/backtesting_parameter```
```
{
  "from_date": "2017-01-01",
  "to_date": "2019-01-01",
  "sell_fee": 0.0006,
  "buy_fee": 0.0006,
  "risk_fee_rate": 0.03,
  "no_stock": 3,
  "combination": ["turnover-inv", "gm"],
  "rsi_look_back": 60,
  "rsi_lb": 0.6,
  "rsi_ub": 0.7,
  "liquidity_look_back": 20,
  "liquidity_lb": 1e6,
  "liquidity_ub": 5e6
}
```
## Evaluation
To print and export the metric images, run the ```metrics.py``` file.
```
python metrics.py
```
## Unit testing
- For testing all function, run the command. The duration for the testing of all functions is nearly 200 second. 
```
python -m unittest
```
- For testing a group of function
```
python -m unittest test/test_financial.py
```
# Optimization
- Optuna is used for the optimization process. More detail of optuna can be found [here](https://optuna.org/)
- The setting of the optimization is stored in file ```parameter/optimization_parameter```
```
{
  "from_date": "2017-01-01",
  "to_date": "2019-01-01",
  "financial_ratios": ["eps", "quick-ratio", "gm", "roe", "turnover-inv"],
  "rsi_range": [0.6, 0.7],
  "liquidity_rank": [1e6, 5e6],
  "no_trial": 10000
}
```