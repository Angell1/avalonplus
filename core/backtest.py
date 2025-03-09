import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import TradingStrategy
from .data_loader import DataLoader

class BacktestEngine:
    def __init__(self, 
                 data_loader: DataLoader,
                 strategy: TradingStrategy,
                 initial_capital: float = 100000.0):
        self.data_loader = data_loader
        self.strategy = strategy
        self.initial_capital = initial_capital
        self._prepare_metrics()

    def _prepare_metrics(self):
        self.metrics = {
            'total_return': 0.0,
            'annualized_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0
        }

    def run_backtest(self, 
                    ticker: str,
                    start_date: str,
                    end_date: str) -> Dict[str, Any]:
        """
        执行回测流程
        :param ticker: 标的代码
        :param start_date: 回测开始日期
        :param end_date: 回测结束日期
        :return: 回测结果字典
        """
        data = self.data_loader.load_historical_data(ticker, start_date, end_date)
        if data is None:
            raise ValueError(f"无法加载{ticker}的历史数据")

        processed_data = self.strategy.prepare_data(data)
        signals = self.strategy.generate_signals(processed_data)
        
        # 生成持仓和交易记录
        portfolio = self._simulate_trading(processed_data, signals)
        
        # 计算风险指标
        risk = self.strategy.calculate_risk(portfolio)
        
        # 计算绩效指标
        self._calculate_performance(portfolio)
        
        return {
            'portfolio': portfolio,
            'metrics': self.metrics,
            'risk_assessment': risk
        }

    def _simulate_trading(self, data: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
        """模拟实际交易流程"""
        positions = pd.DataFrame(index=data.index)
        positions['signal'] = signals
        positions['position'] = positions['signal'].shift(1)
        positions['cash'] = self.initial_capital
        positions['holdings'] = 0.0
        positions['total'] = self.initial_capital
        
        # 实现具体的交易逻辑
        for i in range(1, len(positions)):
            prev_position = positions['position'].iloc[i-1]
            curr_position = positions['position'].iloc[i]
            
            if curr_position != prev_position:
                # 计算交易数量（全仓进出）
                price = data['Close'].iloc[i]
                trade_size = positions['cash'].iloc[i-1] / price
                
                # 计算交易成本（0.1%佣金）
                commission = trade_size * price * 0.001
                
                if curr_position == 1:
                    # 买入操作
                    positions['holdings'].iloc[i] = trade_size
                    positions['cash'].iloc[i] = positions['cash'].iloc[i-1] - trade_size * price - commission
                elif curr_position == -1:
                    # 卖出操作
                    positions['holdings'].iloc[i] = 0
                    positions['cash'].iloc[i] = positions['cash'].iloc[i-1] + trade_size * price - commission
                else:
                    # 持仓不变
                    positions['holdings'].iloc[i] = positions['holdings'].iloc[i-1]
                    positions['cash'].iloc[i] = positions['cash'].iloc[i-1]
            else:
                # 持仓不变
                positions['holdings'].iloc[i] = positions['holdings'].iloc[i-1]
                positions['cash'].iloc[i] = positions['cash'].iloc[i-1]
            
            # 计算总资产
            positions['total'].iloc[i] = positions['cash'].iloc[i] + positions['holdings'].iloc[i] * data['Close'].iloc[i]
        
        return positions

    def _calculate_performance(self, portfolio: pd.DataFrame):
        """计算关键绩效指标"""
        returns = portfolio['total'].pct_change().dropna()
        
        self.metrics['total_return'] = portfolio['total'][-1] / self.initial_capital - 1
        self.metrics['annualized_return'] = np.power(1 + self.metrics['total_return'], 252/len(returns)) - 1
        
        peak = portfolio['total'].cummax()
        drawdown = (portfolio['total'] - peak) / peak
        self.metrics['max_drawdown'] = drawdown.min()
        
        self.metrics['sharpe_ratio'] = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        winning_trades = len(returns[returns > 0])
        self.metrics['win_rate'] = winning_trades / len(returns) if len(returns) > 0 else 0