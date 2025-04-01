![Static Badge](https://img.shields.io/badge/PLUTUS-verified_95%25-green)
# Abstract
The objective of this project is to examine the relationship between financial signals and the buy-and-hold return rate. Specifically, the study will focus on sorting firms based on their financial statement and selecting entry points using technical signals. Each day, three stocks will be selected for purchase, with the positions held for a three-month trading period.
# Introduction
This project recommends 3 stocks daily in the Vietnam market by utilizing fundamental signals and technical signals calculated from financial statement and daily price data respectively. The stocks are hold in 60 trading days period.

## Feature
- [x] Generate Mock Data for unit testing 
- [x] Validate Test Case: Financial, Technical Signal and Backtesting
- [x] Optimize hyperparameters
- [x] Evaluate backtesting and optimization
- [ ] Paper trade

## Installation
- Requirement: pip, virtualenv
- Create and source new virtual environment in the current working directory with command
```
python3 -m virtualenv venv
source venv/bin/activate
```
- Install the dependencies by:
```
pip install -r requirements.txt
```

# Related Work (Background)
The project examines various types of resources to identify efficient financial ratios. For many years, numerous studies have explored the relationship between abnormal returns and fundamental analysis strategies. Jeffery and Brian introduced their financial ratios in their work Abnormal Returns to a Fundamental Analysis Strategy (see [link](https://www.jstor.org/stable/248340)). The use of financial ratios remains relevant today and is commonly referred to as smart beta (see [link](https://hub.algotrade.vn/knowledge-hub/phuong-phap-trong-so-duoc-su-dung-trong-chien-luoc-beta-vuot-troi/)).

# Data
There are two types of data which are the financial statement and daily trading data. For the calculation, the data is collected from:
- start date: the beginning date of daily data includeing the look back data for the signal calculation
- end date: the end date of daily data including the last date for the return calculation
- RSI upper bound and lower bound are in range [0, 1]
- Liquidity upper bound, lower bound and step are amount in VND devide by 1000

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
- If you don't create ```.env``` file then the code will use data in ```mock``` folder
- Change the name of the ```stat-example``` folder to ```stat``` or create a new one with the same structure
- By default the code is run with file mode. To specify the path of the data file:
  - Create ```mock``` folder
  - Download and extract the in-sample, out-sample data files and place it in this folder [Link](https://drive.google.com/drive/folders/11YOHtzsivwJsOG23PbCyhlJjxroaR_zP?usp=drive_link)

## Data initiation
- To create all required folders run the command
```
python create_folders.py
```
- To create the daily asset data with backtesting parameter run the ```main.py``` file
```
python main.py
```
- The daily asset data will be stored in folder ```stat/in-sample/asset```. 

# Implementation
- We filter out the firms by the recommended financial ratios with its liquidity
- The financial ratios include:
  - eps
  - quick ratio
  - gross margin
  - roe
  - turnover inventory
- The portfolio in each day also depends on the exponential RSI indicator

# In-sample Backtesting
- To print and export the metric images, run the ```metrics.py``` file with ```backtesting``` mode.
```
python metrics.py backtesting
```
- [Sharpe ratio](stat-example/in-sample/sharpe/combine.png), [acummilative return](stat-example/in-sample/ar/combine.png) and [Number of stock each day](sta-example/in-sample/no-stocks/combine.png) are stored in ```stat/in-sample``` folder.
- The parameters of backtesting is stored in file ```parameter/backtesting_parameter.json```
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
- The console will print the result of metrics of combinanation of financial ratios
  
<center>

|           | ESR   | MMMD     | PPP     | MAR     | MIR      | MER    | EMR    |
|-----------|-------|----------|---------|---------|----------|--------|--------|
| Portfolio | 0.229 | -9.160%  | 52.644% | 54.834% | -32.122% | 2.157% | 0.597% |
| Index     | 1.512 | -25.319% | 67.807% | 33.306% | -25.319% | 4.281% | 1.305% |

</center>

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

# Out-of-sample Backtesting
For validation the out sample data, modify the ```os_from_date``` and ```os_to_date``` in the ```optimization_parameter.json``` file and run 
```
python validation.py
```
-  The asset result will be stored in ```stat/out-sample/asset``` the same as backtesting process.
- The setting of the validation is stored in file ```parameter/optimization_parameter.json```
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
- To get the metric of these result run the command metric with ```validation``` mode
```
python metrics.py validation
```
- With random seed is 2024 the output of the validation in optimized parameters are:

<center>
  
|           | ESR    | MMMD     | PPP     | MAR     | MIR      | MER     | EMR     |
|-----------|--------|----------|---------|---------|----------|---------|---------|
| [7, 9]    | -1.015 | -7.021%  | 29.411% | 11.725% | -14.392% | -1.870% | -1.182% |
| [7, 10]   | -0.455 | -6.531%  | 40.384% | 11.725% | -14.392% | -0.425% | -0.571% |
| [7, 9.5]  | -0.760 | -6.713%  | 33.695% | 11.725% | -14.392% | -1.256% | -0.893% |
| [6.5, 9]  | -1.241 | -6.920%  | 27.731% | 11.725% | -14.392% | -2.193% | -0.973% |
| [6.5, 9.5]| -1.043 | -6.700%  | 30.952% | 11.725% | -14.392% | -1.726% | -0.774% |
| Index     | -0.578 | -33.511% | 18.548% | 12.376% | -31.291% | -1.580% | -0.385% |

</center>


# Conclusion
Although the financial ratios are selected from various sources, they have proven to be inefficient in the Vietnamese market. The strategy of benchmarking the portfolio should be refined, moving beyond the use of average values. 

# Reference
- [1] Jeffery S. Abarbanell, Brian J. Bushee. "Abnormal Returns to a Fundamental Analysis Strategy", The Accounting Review, Vol. In: 73, No. 1 (Jan., 1998), pp. 19-45
- [2] Victor L. Bernard, Jacob K. Thomas. "Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?". In: Journal of Accounting Research, Vol. 27, Current Studies on The Information Content of Accounting Earnings (1989), pp. 1-36
- [3] Algotrade. Weighting Methods Used in Smart-Beta Strategy. [Link](https://hub.algotrade.vn/knowledge-hub/weighting-methods-used-in-smart-beta-strategy/)
