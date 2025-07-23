import requests
import pandas as pd
import time

def fetch_okx_candles(symbol="BTC-USDT", start_time="2022-01-01", end_time="2025-07-01", bar="4H"):
    url = "https://www.okx.com/api/v5/market/candles"
    start_ts = int(pd.to_datetime(start_time).timestamp() * 1000)
    end_ts = int(pd.to_datetime(end_time).timestamp() * 1000)
    all_data = []

    while start_ts < end_ts:
        params = {
            "instId": symbol,
            "bar": bar,
            "before": end_ts,
            "limit": 100,
        }
        resp = requests.get(url, params=params).json()
        if resp["code"] != "0" or not resp["data"]:
            print("Error:", resp)
            break

        data = resp["data"]
        all_data.extend(data)
        end_ts = int(data[-1][0]) - 1  # 向前推进

        time.sleep(0.3)

    df = pd.DataFrame(all_data, columns=[
        "ts", "open", "high", "low", "close", "vol", "volCcy", "volCcyQuote", "confirm"
    ])
    df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
    df = df.sort_values("ts")
    df.to_csv(f"{symbol.replace('-', '_')}_{bar}.csv", index=False)
    print(f"保存完成，共 {len(df)} 条数据")

# 示例调用
fetch_okx_candles(
    symbol="BTC-USDT",
    start_time="2022-01-01",
    end_time="2025-07-01",
    bar="4H"
)

