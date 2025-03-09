from core.base_strategy import TradingStrategy
import pandas as pd
import numpy as np

class MovingAverageCrossStrategy(TradingStrategy):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self.short_window = parameters.get('short_window', 20)
        self.long_window = parameters.get('long_window', 50)

    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data['short_ma'] = data['Close'].rolling(self.short_window).mean()
        data['long_ma'] = data['Close'].rolling(self.long_window).mean()
        return data.dropna()

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        data['signal'] = np.where(
            data['short_ma'] > data['long_ma'], 
            1,  # 买入信号
            np.where(
                data['short_ma'] < data['long_ma'],
                -1,  # 卖出信号
                0  # 持仓
            )
        )
        return data['signal']

    def optimize_parameters(self, data: pd.DataFrame) -> dict:
        best_sharpe = -np.inf
        best_params = {'short_window': 20, 'long_window': 50}
        
        # 参数搜索范围
        short_windows = range(10, 50, 5)
        long_windows = range(50, 200, 10)
        
        for short in short_windows:
            for long in long_windows:
                if short >= long:
                    continue
                
                # 计算策略收益
                data['signal'] = np.where(data['Close'].rolling(short).mean() > data['Close'].rolling(long).mean(), 1, -1)
                returns = data['Close'].pct_change() * data['signal'].shift(1)
                returns = returns.dropna()
                
                # 计算夏普比率
                sharpe = np.sqrt(252) * returns.mean() / returns.std()
                
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = {'short_window': short, 'long_window': long}
        
        return best_params

    def calculate_risk(self, data: pd.DataFrame) -> float:
        # 计算最大回撤作为风险指标
        returns = data['Close'].pct_change()
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding().max()
        return (cumulative/peak - 1).min()

    def performance_metrics(self, data: pd.DataFrame) -> dict:
        # 计算策略特有指标
        returns = data['Close'].pct_change().dropna()
        return {
            'annual_return': np.prod(1 + returns) ** (252/len(returns)) - 1,
            'volatility': returns.std() * np.sqrt(252)
        }