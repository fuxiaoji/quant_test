# readme

## 前面
本人纯新手，误入金融专业的游戏爱好者，对量化，游戏开发感兴趣，欢迎交流(*´∀ ˋ*) (*´∀ ˋ*) (*´∀ ˋ*) 
## 项目简介

本项目包含两个主要部分：

1. **LLM（大模型接口）**：通过 OpenAI SDK 调用 DeepSeek Chat API，实现自然语言交互。
2. **量化轮动策略**：基于动量轮动思想，自动获取ETF历史数据，计算动量指标，回测并可视化策略表现。

## 目录结构

```
api.txt                # OpenAI/DeepSeek API密钥
LLM/
    request_llm.py     # LLM接口请求代码
    test_llm.py        # LLM交互测试脚本
quant_part/
    etf_data.py        # ETF数据获取
    plot_nav.py        # 策略净值曲线绘制
    quant_test.py      # 量化轮动策略主程序
    report_detail.py   # 策略绩效统计与结果展示
    tttt.py            # ETF数据字段测试脚本
```

## 环境依赖

- Python >= 3.8
- 主要依赖库：
  - akshare
  - pandas
  - numpy
  - matplotlib
  - scikit-learn
  - quantstats
  - openai

安装依赖：
```sh
pip install akshare pandas numpy matplotlib scikit-learn quantstats openai
```

## 使用方法

### 1. LLM接口测试

进入 `LLM` 目录，运行：
```sh
python test_llm.py
```
根据提示输入问题，模型将返回答案。API密钥默认读取 `api.txt` 内容。

### 2. 量化轮动策略回测

进入 `quant_part` 目录，运行：
```sh
python quant_test.py
```
自动获取ETF历史数据，计算动量指标，回测轮动策略，并输出绩效统计及净值曲线。

## 主要功能说明

- ETF历史数据自动获取与合并
- 动量指标计算（涨幅、斜率得分）
- 轮动信号生成与策略回测
- 策略绩效统计（收益率、波动率、夏普比率、最大回撤等）
- 策略净值曲线可视化

## 联系方式
我的qq1105793864
如有问题或建议，请提交 Issue 或联系项目维护者。
