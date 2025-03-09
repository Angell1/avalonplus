import pandas as pd
import numpy as np

# 实现RSI超买指标计算函数：
# 1. 采用RSI相对强弱指数算法，使用5日默认周期
# 2. 实现向量化计算逻辑：
#    - 计算每日价格变动delta
#    - 分离上涨收益(gain)和下跌损失(loss)
#    - 使用rolling窗口计算平均涨跌幅
# 3. 内置超买区域判断(RSI>70)
# 4. 输出关键统计指标：
#    - 超买天数
#    - 最大RSI值
#    - 最新RSI值
# 5. 保持与现有`CalculateVolatility` 函数一致的DataFrame输入格式
# 6. 支持参数化周期设置，增强策略灵活性
def CalculateOverbought(data, period=5):
    """
    RSI超买指标计算函数
    
    参数:
    data: 包含收盘价数据的DataFrame，需包含'close'列
    period: 计算周期，默认5日
    
    返回:
    rsi: 包含RSI值的Series
    """
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # 计算滚动平均增益/损失
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    # 计算相对强度RS
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    # 输出超买统计信息
    overbought = rsi > 70
    risk_level = '低风险' if rsi <50 \
    else '中风险' if rsi <70 else '高风险'
    print(f"超买区域天数（RSI>70）: {overbought.sum()}日")
    print(f"最大RSI值: {rsi.max():.2f}")
    print(f"最新RSI({period}日): {rsi.iloc[-1]:.2f}")
    print(f"RSI超买指标 估值风险等级: {risk_level}")

    return rsi


# 指数估值风险评估
# - 历史分位数计算 ：采用滚动窗口计算PE/PB指标的5年历史分位数
# - 风险溢价模型 ：结合3%无风险利率计算股权风险溢价
# - 三级预警机制 ：设置30%/70%/90%分位阈值对应低/中/高风险等级
# - 标准化输出 ：输出当前PE值、历史分位点和风险等级
def CalculateValuationRisk(data, period=60):
    # 采用市盈率分位数法结合风险溢价模型
    # 参数:
    # data - 包含PE/PB指标的DataFrame
    # period - 历史分析周期（默认5年）
    # 计算历史分位数
    data['PE_quantile'] = data['PE'].rolling(window=period*12).apply(
        lambda x: (x.rank(pct=True).iloc[-1]), raw=False)
    data['PB_quantile'] = data['PB'].rolling(window=period*12).apply(
        lambda x: (x.rank(pct=True).iloc[-1]), raw=False)

    # 风险溢价计算（假设无风险利率3%）
    risk_free_rate = 0.03
    equity_risk_premium = 1/data['PE'].iloc[-1] - risk_free_rate

    # 三级预警阈值
    current_pe_q = data['PE_quantile'].iloc[-1]
    risk_level = '低风险' if current_pe_q <0.3 \
        else '中风险' if current_pe_q <0.7 else '高风险'

    # 输出关键指标
    print(f"当前PE: {data['PE'].iloc[-1]:.2f} 历史分位: {current_pe_q:.1%}")
    print(f"股权风险溢价: {equity_risk_premium:.2%}")
    print(f"指数估值风险 估值风险等级: {risk_level}")

    return risk_level