# README

## Introduction

I'm a complete beginner, a game enthusiast who accidentally entered the finance major. Interested in quantitative trading and game development. Welcome to communicate (*´∀ ˋ*) (*´∀ ˋ*) (*´∀ ˋ*)

## Project Overview

This project contains two main modules:

1. **LLM (Large Language Model Interface)**: Uses the OpenAI SDK to call the DeepSeek Chat API for natural language interaction.
2. **Quantitative Rotation Strategy**: Based on momentum rotation, automatically fetches ETF historical data, calculates momentum indicators, backtests, and visualizes strategy performance.

## Directory Structure

```
api.txt                # OpenAI/DeepSeek API key
LLM/
    request_llm.py     # LLM API request code
    test_llm.py        # LLM interaction test script
quant_part/
    etf_data.py        # ETF data fetching
    plot_nav.py        # Strategy NAV curve plotting
    quant_test.py      # Main rotation strategy script
    report_detail.py   # Strategy performance statistics and reporting
    tttt.py            # ETF data field test script
```

## Environment Requirements

- Python >= 3.8
- Main dependencies:
  - akshare
  - pandas
  - numpy
  - matplotlib
  - scikit-learn
  - quantstats
  - openai

Install dependencies:
```sh
pip install akshare pandas numpy matplotlib scikit-learn quantstats openai
```

## Usage

### 1. LLM Interface Test

Go to the `LLM` directory and run:
```sh
python test_llm.py
```
Enter your question as prompted, and the model will return an answer. The API key is read from `api.txt` by default.

### 2. Quantitative Rotation Strategy Backtest

Go to the `quant_part` directory and run:
```sh
python quant_test.py
```
ETF historical data will be fetched automatically, momentum indicators calculated, the rotation strategy backtested, and performance statistics and NAV curve will be displayed.

## Main Features

- Automatic ETF data fetching and merging
- Momentum indicator calculation (return, slope score)
- Rotation signal generation and strategy backtesting
- Strategy performance statistics (return, volatility, Sharpe ratio, max drawdown, etc.)
- Strategy NAV curve visualization

## Contact

My QQ: 1105793864  
If you have any questions or suggestions, please submit an Issue or contact the project maintainer.
thank you!