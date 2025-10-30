# ai_strategies.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class StrategyConfig:
    """策略配置"""
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: str  # LOW, MEDIUM, HIGH

@dataclass
class StrategyResult:
    """策略分析结果"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    target_price: float
    stop_loss: float
    reasoning: str
    strategy_name: str

class AIBaseStrategy:
    """AI策略基类"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.name = config.name
        self.risk_level = config.risk_level
    
    async def analyze(self, symbol: str, market_data: Dict) -> StrategyResult:
        """分析股票并生成交易信号"""
        raise NotImplementedError("子类必须实现此方法")
    
    def calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        if len(price_data) < 20:
            return {}
        
        closes = price_data['close']
        highs = price_data['high']
        lows = price_data['low']
        volumes = price_data['volume']
        
        # 简单移动平均
        sma_20 = closes.rolling(20).mean().iloc[-1]
        sma_50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else closes.mean()
        
        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)) if not pd.isna(rs.iloc[-1]) else 50
        
        # MACD
        exp1 = closes.ewm(span=12).mean()
        exp2 = closes.ewm(span=26).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9).mean()
        
        return {
            'sma_20': float(sma_20),
            'sma_50': float(sma_50),
            'rsi': float(rsi.iloc[-1]) if not isinstance(rsi, float) else rsi,
            'macd': float(macd.iloc[-1]),
            'macd_signal': float(signal_line.iloc[-1]),
            'current_price': float(closes.iloc[-1])
        }

class DeepSeekMomentumStrategy(AIBaseStrategy):
    """DeepSeek动量策略"""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        # 这里可以初始化DeepSeek API客户端
        # self.client = DeepSeekClient(config.parameters.get('api_key'))
    
    async def analyze(self, symbol: str, market_data: Dict) -> StrategyResult:
        """动量策略分析"""
        try:
            # 模拟AI分析过程
            await asyncio.sleep(0.5)  # 模拟API调用延迟
            
            # 获取技术指标
            tech_indicators = self.calculate_technical_indicators(market_data.get('price_data', pd.DataFrame()))
            
            if not tech_indicators:
                return StrategyResult(
                    symbol=symbol,
                    action="HOLD",
                    confidence=0.5,
                    target_price=0,
                    stop_loss=0,
                    reasoning="数据不足，无法分析",
                    strategy_name=self.name
                )
            
            # 动量策略逻辑
            current_price = tech_indicators['current_price']
            rsi = tech_indicators['rsi']
            sma_20 = tech_indicators['sma_20']
            macd = tech_indicators['macd']
            macd_signal = tech_indicators['macd_signal']
            
            # 简单的动量判断
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI判断
            if rsi < 30:
                bullish_signals += 1
            elif rsi > 70:
                bearish_signals += 1
            
            # 移动平均判断
            if current_price > sma_20:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # MACD判断
            if macd > macd_signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # 综合判断
            total_signals = bullish_signals + bearish_signals
            confidence = abs(bullish_signals - bearish_signals) / total_signals if total_signals > 0 else 0.5
            
            if bullish_signals > bearish_signals:
                action = "BUY"
                target_price = current_price * 1.1  # 目标上涨10%
                stop_loss = current_price * 0.95    # 止损5%
                reasoning = f"动量策略检测到{bullish_signals}个看涨信号，{bearish_signals}个看跌信号"
            elif bearish_signals > bullish_signals:
                action = "SELL"
                target_price = current_price * 0.9   # 目标下跌10%
                stop_loss = current_price * 1.05     # 止损5%
                reasoning = f"动量策略检测到{bullish_signals}个看涨信号，{bearish_signals}个看跌信号"
            else:
                action = "HOLD"
                target_price = current_price
                stop_loss = current_price * 0.98
                reasoning = "动量信号均衡，建议观望"
            
            return StrategyResult(
                symbol=symbol,
                action=action,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning,
                strategy_name=self.name
            )
            
        except Exception as e:
            return StrategyResult(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                target_price=0,
                stop_loss=0,
                reasoning=f"分析过程中出错: {str(e)}",
                strategy_name=self.name
            )

class QWenMeanReversionStrategy(AIBaseStrategy):
    """通义千问均值回归策略"""
    
    async def analyze(self, symbol: str, market_data: Dict) -> StrategyResult:
        """均值回归策略分析"""
        try:
            await asyncio.sleep(0.5)  # 模拟API调用延迟
            
            tech_indicators = self.calculate_technical_indicators(market_data.get('price_data', pd.DataFrame()))
            
            if not tech_indicators:
                return StrategyResult(
                    symbol=symbol,
                    action="HOLD",
                    confidence=0.5,
                    target_price=0,
                    stop_loss=0,
                    reasoning="数据不足，无法分析",
                    strategy_name=self.name
                )
            
            current_price = tech_indicators['current_price']
            sma_20 = tech_indicators['sma_20']
            rsi = tech_indicators['rsi']
            
            # 均值回归逻辑
            price_deviation = (current_price - sma_20) / sma_20
            
            if price_deviation < -0.05 and rsi < 35:  # 价格低于均线5%且RSI超卖
                action = "BUY"
                confidence = min(0.8, abs(price_deviation) * 10)
                target_price = sma_20  # 回归到均线
                stop_loss = current_price * 0.92
                reasoning = f"价格偏离均线{price_deviation:.2%}，出现均值回归机会"
            elif price_deviation > 0.05 and rsi > 65:  # 价格高于均线5%且RSI超买
                action = "SELL"
                confidence = min(0.8, abs(price_deviation) * 10)
                target_price = sma_20  # 回归到均线
                stop_loss = current_price * 1.08
                reasoning = f"价格偏离均线{price_deviation:.2%}，可能出现回调"
            else:
                action = "HOLD"
                confidence = 0.3
                target_price = current_price
                stop_loss = current_price * 0.98
                reasoning = "价格在正常波动范围内，建议观望"
            
            return StrategyResult(
                symbol=symbol,
                action=action,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning,
                strategy_name=self.name
            )
            
        except Exception as e:
            return StrategyResult(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                target_price=0,
                stop_loss=0,
                reasoning=f"分析过程中出错: {str(e)}",
                strategy_name=self.name
            )

class MultiAIConsensusStrategy(AIBaseStrategy):
    """多AI模型共识策略"""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.sub_strategies = []
        
    def add_strategy(self, strategy: AIBaseStrategy):
        """添加子策略"""
        self.sub_strategies.append(strategy)
    
    async def analyze(self, symbol: str, market_data: Dict) -> StrategyResult:
        """多策略共识分析"""
        if not self.sub_strategies:
            return StrategyResult(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                target_price=0,
                stop_loss=0,
                reasoning="没有可用的子策略",
                strategy_name=self.name
            )
        
        # 运行所有子策略
        tasks = [strategy.analyze(symbol, market_data) for strategy in self.sub_strategies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        buy_count = 0
        sell_count = 0
        hold_count = 0
        valid_results = []
        total_confidence = 0
        
        for result in results:
            if isinstance(result, Exception) or not hasattr(result, 'action'):
                continue
                
            valid_results.append(result)
            total_confidence += result.confidence
            
            if result.action == "BUY":
                buy_count += 1
            elif result.action == "SELL":
                sell_count += 1
            else:
                hold_count += 1
        
        if not valid_results:
            return StrategyResult(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                target_price=0,
                stop_loss=0,
                reasoning="所有子策略分析失败",
                strategy_name=self.name
            )
        
        # 共识决策
        total_strategies = len(valid_results)
        buy_ratio = buy_count / total_strategies
        sell_ratio = sell_count / total_strategies
        
        avg_confidence = total_confidence / len(valid_results)
        
        if buy_ratio >= 0.6:  # 60%策略建议买入
            action = "BUY"
            confidence = avg_confidence * buy_ratio
            reasoning = f"{buy_count}/{total_strategies}个策略建议买入"
        elif sell_ratio >= 0.6:  # 60%策略建议卖出
            action = "SELL"
            confidence = avg_confidence * sell_ratio
            reasoning = f"{sell_count}/{total_strategies}个策略建议卖出"
        else:
            action = "HOLD"
            confidence = 0.5
            reasoning = f"策略分歧：{buy_count}买入, {sell_count}卖出, {hold_count}观望"
        
        # 计算平均目标价和止损
        target_prices = [r.target_price for r in valid_results if r.target_price > 0]
        stop_losses = [r.stop_loss for r in valid_results if r.stop_loss > 0]
        
        avg_target = sum(target_prices) / len(target_prices) if target_prices else 0
        avg_stop_loss = sum(stop_losses) / len(stop_losses) if stop_losses else 0
        
        return StrategyResult(
            symbol=symbol,
            action=action,
            confidence=confidence,
            target_price=avg_target,
            stop_loss=avg_stop_loss,
            reasoning=reasoning,
            strategy_name=self.name
        )