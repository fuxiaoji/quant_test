import akshare as ak

# 测试用一个ETF代码
test_df = ak.fund_etf_hist_em(symbol="510300", start_date="20230701", end_date="20230731")
print(test_df.columns)
print(test_df.head())
