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
- RSI upper bound and lower bound are in range [0, 1]
- Liquidity upper bound, lower bound and step are amount in VND devide by 1000
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
- Paramters are stored in ```parameter/backtesting_parameter.json```
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
- We use sharpe ratio as our objective function
- The setting of the optimization is stored in file ```parameter/optimization_parameter.json```
```
{
  "from_date": "2017-01-01",
  "to_date": "2019-01-01",
  "os_from_date": "2019-01-02",
  "os_to_date": "2021-12-31",
  "rsi_lb": 0.6,
  "rsi_ub": 0.7,
  "combination": ["turnover-inv", "gm"],
  "step": 5e5,
  "llb_low": 1e6,
  "llb_high": 7e6,
  "delta_low": 5e5,
  "delta_high": 3e6,
  "trial": 20
}
```
- Run the command below for optimization
```
python optimization.py
```
- The result of optimization is stored at ```stat/optimization.log.csv```
- Each itteration in the process takes nearly 2s => 1000 trials will take a half of hour
- For validation the out sample data, modify the ```os_from_date``` and ```os_to_date``` in the ```optimization_parameter.json``` file and run 
```
python validation.py
```
-  The asset result will be stored in ```stat/asset``` the same as backtesting process.
- To get the metric of these result run the command metric again
```
python metrics.py
```