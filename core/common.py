from risk_manager import risk_strategy

# // 判断市场过去一段时间内的趋势（下跌、震荡、上涨）
# 1个月内市场强势（超过平均成交量占比、（下跌交易日占比）收盘价格-开盘价格、连续下跌持续交易日（）、连续上涨持续交易日（））
# 2个月内市场强势（超过平均成交量占比、（下跌交易日占比）收盘价格-开盘价格、连续下跌持续交易日（）、连续上涨持续交易日（））
# 3个月内市场强势（超过平均成交量占比、（下跌交易日占比）收盘价格-开盘价格、连续下跌持续交易日（）、连续上涨持续交易日（））
# args:
# 1、交易数据:pandas.core.frame.DataFrame对象
def IsStrong(DfData):
    print(DfData.columns)#查看列下标
    # 计算平均成交量，超过平均成交量占比
    DescribeDfData = DfData.describe()
    print("DF 行数：",DfData.shape[0])
    print("DF 列数：",DfData.shape[1])
    print("指标计算起始时间-截止时间：",DfData["trade_date"][0],DfData["trade_date"][DfData.shape[0]-1])
    print("最大收盘价：",DescribeDfData["close"]["max"])
    print("最小收盘价：",DescribeDfData["close"]["min"])
    print("平均收盘价：",DescribeDfData["close"]["mean"])
    print("最大价差：", DescribeDfData["close"]["max"]-DescribeDfData["close"]["min"])
    print("最大交易量：",DescribeDfData["volume"]["max"])
    print("最小交易量：",DescribeDfData["volume"]["min"])
    print("平均交易量：",DescribeDfData["volume"]["mean"])
    print("最大交易量差值：", DescribeDfData["volume"]["max"]-DescribeDfData["volume"]["min"])
    print("25%交易日收盘价分位数：",DescribeDfData["close"]["25%"])
    print("50%交易日收盘价分位数：",DescribeDfData["close"]["50%"])
    print("75%交易日收盘价分位数：",DescribeDfData["close"]["75%"])

    DfData = markhammerandhanging(DfData)

    # 交易日占比，收盘价格-开盘价格
    ChangeRatio(DfData)

    # 交易日成交量超过平均成交量占比
    VolumeRatio(DfData)

    risk_strategy.CalculateVaR(DfData)
    risk_strategy.CalculateVolatility(DfData)
    # increasing_trends, decreasing_trends = identify_trends(DfData,22)
    # print(increasing_trends,decreasing_trends)




# mark
# 锤子线：出现在下跌趋势中，实体较小，下影线至少是实体的两倍长，几乎没有上影线。
# 上吊线：出现在上涨趋势中，实体较小，下影线至少是实体的两倍长，几乎没有上影线。
def markhammerandhanging(DfData):
    # 计算实体长度
    DfData['body_length'] = abs(DfData['close'] - DfData['open'])

    # 计算上下影线长度
    DfData['upper_shadow'] = DfData['high'] - DfData[['close', 'open']].max(axis=1)
    DfData['lower_shadow'] = DfData[['close', 'open']].min(axis=1) - DfData['low']

    # 识别锤子线
    DfData['is_hammer'] = (DfData['body_length'] < 0.5 * DfData['lower_shadow']) & \
                      (DfData['upper_shadow'] <= 0.1 * DfData['lower_shadow']) & \
                      (DfData['change_pct'] < 0)  # 下跌趋势中的锤子线

    # 识别上吊线
    DfData['is_hanging_man'] = (DfData['body_length'] < 0.5 * DfData['lower_shadow']) & \
                           (DfData['upper_shadow'] <= 0.1 * DfData['lower_shadow']) & \
                           (DfData['change_pct'] > 0)  # 上涨趋势中的上吊线

    return DfData


# 我们首先计算 high 和 low 列的差值。
# 然后，窗口大小参数 window_size 用于检查一段时间内的数据。你可以根据需求调整窗口大小。
# 对于 increasing_trends，我们检查窗口内 high 列的差值是否都是正数和 low 列的差值是否都是负数。
# 对于 decreasing_trends，我们检查窗口内 high 列的差值是否都是负数和 low 列的差值是否都是正数。
# 最后，返回上涨和下跌趋势的开始和结束日期。
def identify_trends(df, window_size=5):
    df['close_diff'] = df['close'].diff()        # 计算 close 的差值
    increasing_trends = []
    decreasing_trends = []
    if len(df) < window_size:
        return
    for i in range(len(df) - window_size + 1):
        window = df.iloc[i:i + window_size]
        print("滑动窗口交易区间",window['trade_date'].iloc[0], window['trade_date'].iloc[-1])

        print("滑动窗口",window['close_diff'].sum())
    return increasing_trends, decreasing_trends



#  交易日涨跌占比
def ChangeRatio(DfData):
    DownCount = 0
    UpCount = 0
    for i in range(0,DfData.shape[0]):
        if (DfData["close"][i] - DfData["open"][i]) < 0:
            DownCount += 1
        if (DfData["close"][i] - DfData["open"][i]) >= 0:
            UpCount += 1
    print("运行周期市场上涨交易日占比：",UpCount/DfData.shape[0] * 100)
    print("运行周期市场下跌交易日占比：",DownCount/DfData.shape[0] * 100)


# 交易日成交量超过平均成交量占比
def VolumeRatio(DfData):
    DescribeDfData = DfData.describe()
    DownCount = 0
    UpCount = 0
    for i in range(0,DfData.shape[0]):
        if (DfData["volume"][i] >= DescribeDfData["volume"]["mean"]):
            DownCount += 1
        else:
            UpCount += 1
    print("运行周期市场交易日超过平均交易量占比：",UpCount/DfData.shape[0] * 100)
    print("运行周期市场交易日小于平均交易量占比：",DownCount/DfData.shape[0] * 100)


# 计算最大回撤
def calculate_max_drawdown(DfData):
    """
    计算最大回撤
    :param cumulative_returns: 累计收益率序列
    :return: 最大回撤
    """
    # 计算收盘价的累计收益率
    DfData['cumulative_return'] = (DfData['close'] / DfData['close'].iloc[0] - 1)
    peak = DfData['cumulative_return'].cummax()
    drawdown = (peak - DfData['cumulative_return']) / peak
    max_drawdown = drawdown.max()
    print("运行周期市场交易日最大回撤：",max_drawdown)
    return max_drawdown



import adata


adata.stock.market.get_market_index()
# k_type: k线类型：1.日；2.周；3.月 默认：1 日k
df1 = adata.stock.market.get_market_index("000001",start_date='2016-06-01')

IsStrong(df1)