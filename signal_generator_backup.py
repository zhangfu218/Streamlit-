# signal_generator.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

@dataclass
class TradeSignal:
    """交易信号"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0-1之间的置信度
    target_price: float
    stop_loss: float
    quantity: int = 0
    timestamp: datetime = None
    reasoning: str = ""
    source: str = ""  # 信号来源
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SignalGenerator:
    """信号生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ai_analyzer = AIAnalyzer(config.get('ai_models', []))
        
        # 权重配置
        self.weights = config.get('weights', {
            'technical': 0.25,
            'fundamental': 0.30,
            'sentiment': 0.15,
            'ai': 0.30
        })
    
    async def generate_trade_signals(self, symbols: List[str]) -> List[TradeSignal]:
        """为多个股票生成交易信号"""
        signals = []
        
        for symbol in symbols:
            signal = await self.generate_single_signal(symbol)
            if signal and signal.action != "HOLD":
                signals.append(signal)
        
        # 按置信度排序
        signals.sort(key=lambda x: x.confidence, reverse=True)
        return signals
    
    async def generate_single_signal(self, symbol: str) -> TradeSignal:
        """为单个股票生成交易信号"""
        try:
            # 获取市场数据（这里需要实际的数据源）
            market_data = await self.get_market_data(symbol)
            
            if not market_data:
                return TradeSignal(
                    symbol=symbol,
                    action="HOLD",
                    confidence=0.0,
                    target_price=0,
                    stop_loss=0,
                    reasoning="无法获取市场数据"
                )
            
            # 多维度分析
            technical_signal = await self.technical_analysis(symbol, market_data)
            fundamental_signal = await self.fundamental_analysis(symbol, market_data)
            sentiment_signal = await self.sentiment_analysis(symbol, market_data)
            ai_signal = await self.ai_analysis(symbol, market_data)
            
            # 信号融合
            combined_signal = self.fuse_signals([
                technical_signal, fundamental_signal, 
                sentiment_signal, ai_signal
            ])
            
            # 应用风险过滤器
            filtered_signal = self.apply_risk_filters(combined_signal, market_data)
            
            return filtered_signal
            
        except Exception as e:
            return TradeSignal(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                target_price=0,
                stop_loss=0,
                reasoning=f"信号生成错误: {str(e)}"
            )
    
    async def technical_analysis(self, symbol: str, market_data: Dict) -> TradeSignal:
        """技术分析"""
        try:
            price_data = market_data.get('price_data')
            if price_data is None or len(price_data) < 20:
                return self.create_hold_signal(symbol, "技术数据不足")
            
            # 计算技术指标
            indicators = self.technical_analyzer.calculate_indicators(price_data)
            
            # 技术分析逻辑
            score = 0.5  # 中性起始分数
            reasoning = []
            
            # 移动平均判断
            if indicators.get('sma_20', 0) > indicators.get('sma_50', 0):
                score += 0.1
                reasoning.append("短期均线上穿长期均线")
            else:
                score -= 0.1
                reasoning.append("短期均线下穿长期均线")
            
            # RSI判断
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                score += 0.15
                reasoning.append("RSI超卖")
            elif rsi > 70:
                score -= 0.15
                reasoning.append("RSI超买")
            
            # MACD判断
            if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
                score += 0.1
                reasoning.append("MACD金叉")
            else:
                score -= 0.1
                reasoning.append("MACD死叉")
            
            # 生成信号
            current_price = indicators.get('current_price', 0)
            if score >= 0.6:
                action = "BUY"
                target_price = current_price * 1.08
                stop_loss = current_price * 0.94
            elif score <= 0.4:
                action = "SELL"
                target_price = current_price * 0.92
                stop_loss = current_price * 1.06
            else:
                action = "HOLD"
                target_price = current_price
                stop_loss = current_price * 0.98
            
            confidence = abs(score - 0.5) * 2  # 转换为0-1的置信度
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence * self.weights['technical'],
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning="; ".join(reasoning),
                source="technical"
            )
            
        except Exception as e:
            return self.create_hold_signal(symbol, f"技术分析错误: {str(e)}")
    
    async def fundamental_analysis(self, symbol: str, market_data: Dict) -> TradeSignal:
        """基本面分析 - 模拟实现"""
        try:
            # 这里应该集成真实的基本面数据
            await asyncio.sleep(0.1)
            
            # 模拟基本面评分
            fundamental_score = np.random.normal(0.6, 0.2)
            fundamental_score = max(0.1, min(0.9, fundamental_score))
            
            current_price = market_data.get('current_price', 0)
            
            if fundamental_score >= 0.7:
                action = "BUY"
                target_price = current_price * 1.12
                stop_loss = current_price * 0.92
                reasoning = "基本面优秀，估值合理"
            elif fundamental_score <= 0.4:
                action = "SELL" 
                target_price = current_price * 0.88
                stop_loss = current_price * 1.08
                reasoning = "基本面疲弱，估值过高"
            else:
                action = "HOLD"
                target_price = current_price
                stop_loss = current_price * 0.98
                reasoning = "基本面中性"
            
            confidence = abs(fundamental_score - 0.5) * 2
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence * self.weights['fundamental'],
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning,
                source="fundamental"
            )
            
        except Exception as e:
            return self.create_hold_signal(symbol, f"基本面分析错误: {str(e)}")
    
    async def sentiment_analysis(self, symbol: str, market_data: Dict) -> TradeSignal:
        """情绪分析 - 模拟实现"""
        try:
            await asyncio.sleep(0.1)
            
            # 模拟情绪评分
            sentiment_score = np.random.normal(0.5, 0.3)
            sentiment_score = max(0.1, min(0.9, sentiment_score))
            
            current_price = market_data.get('current_price', 0)
            
            if sentiment_score >= 0.6:
                action = "BUY"
                reasoning = "市场情绪积极"
            elif sentiment_score <= 0.4:
                action = "SELL"
                reasoning = "市场情绪消极"
            else:
                action = "HOLD" 
                reasoning = "市场情绪中性"
            
            confidence = abs(sentiment_score - 0.5) * 2
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence * self.weights['sentiment'],
                target_price=current_price,
                stop_loss=current_price * 0.98,
                reasoning=reasoning,
                source="sentiment"
            )
            
        except Exception as e:
            return self.create_hold_signal(symbol, f"情绪分析错误: {str(e)}")
    
    async def ai_analysis(self, symbol: str, market_data: Dict) -> TradeSignal:
        """AI分析"""
        try:
            ai_result = await self.ai_analyzer.analyze(symbol, market_data)
            
            return TradeSignal(
                symbol=symbol,
                action=ai_result.action,
                confidence=ai_result.confidence * self.weights['ai'],
                target_price=ai_result.target_price,
                stop_loss=ai_result.stop_loss,
                reasoning=ai_result.reasoning,
                source="ai"
            )
            
        except Exception as e:
            return self.create_hold_signal(symbol, f"AI分析错误: {str(e)}")
    
    def fuse_signals(self, signals: List[TradeSignal]) -> TradeSignal:
        """多信号融合"""
        if not signals:
            return self.create_hold_signal("", "无有效信号")
        
        # 计算加权投票
        buy_score = 0
        sell_score = 0
        total_confidence = 0
        target_prices = []
        stop_losses = []
        reasoning_parts = []
        
        for signal in signals:
            weight = signal.confidence
            total_confidence += weight
            
            if signal.action == "BUY":
                buy_score += weight
            elif signal.action == "SELL":
                sell_score += weight
            
            if signal.target_price > 0:
                target_prices.append(signal.target_price)
            if signal.stop_loss > 0:
                stop_losses.append(signal.stop_loss)
            
            if signal.reasoning:
                reasoning_parts.append(f"{signal.source}: {signal.reasoning}")
        
        if total_confidence == 0:
            return self.create_hold_signal(signals[0].symbol, "所有信号置信度为0")
        
        # 决定最终动作
        buy_ratio = buy_score / total_confidence
        sell_ratio = sell_score / total_confidence
        
        if buy_ratio >= 0.6:  # 60%权重支持买入
            action = "BUY"
            confidence = buy_ratio
        elif sell_ratio >= 0.6:  # 60%权重支持卖出
            action = "SELL"
            confidence = sell_ratio
        else:
            action = "HOLD"
            confidence = 0.5
        
        # 计算平均目标价和止损
        avg_target = sum(target_prices) / len(target_prices) if target_prices else 0
        avg_stop_loss = sum(stop_losses) / len(stop_losses) if stop_losses else 0
        
        return TradeSignal(
            symbol=signals[0].symbol,
            action=action,
            confidence=confidence,
            target_price=avg_target,
            stop_loss=avg_stop_loss,
            reasoning=" | ".join(reasoning_parts)
        )
    
    def apply_risk_filters(self, signal: TradeSignal, market_data: Dict) -> TradeSignal:
        """应用风险过滤器"""
        # 这里可以添加各种风险过滤规则
        current_price = market_data.get('current_price', 0)
        
        # 示例：如果止损幅度过大，降低置信度
        if signal.action != "HOLD":
            stop_loss_pct = abs(signal.stop_loss - current_price) / current_price
            if stop_loss_pct > 0.15:  # 止损超过15%
                signal.confidence *= 0.7
                signal.reasoning += " (高风险：止损幅度较大)"
        
        return signal
    
    async def get_market_data(self, symbol: str) -> Dict:
        """获取市场数据 - 需要实际的数据源集成"""
        # 这里应该调用真实的数据API
        await asyncio.sleep(0.1)
        
        # 模拟数据
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        prices = np.random.normal(100, 20, 100).cumsum() + 1000
        
        return {
            'symbol': symbol,
            'current_price': float(prices[-1]),
            'price_data': pd.DataFrame({
                'date': dates,
                'open': prices + np.random.normal(0, 5, 100),
                'high': prices + np.random.normal(5, 3, 100),
                'low': prices - np.random.normal(5, 3, 100),
                'close': prices,
                'volume': np.random.randint(1000000, 50000000, 100)
            })
        }
    
    def create_hold_signal(self, symbol: str, reason: str) -> TradeSignal:
        """创建观望信号"""
        return TradeSignal(
            symbol=symbol,
            action="HOLD",
            confidence=0.0,
            target_price=0,
            stop_loss=0,
            reasoning=reason
        )

# 辅助分析类（简化实现）
class TechnicalAnalyzer:
    def calculate_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标 - 简化实现"""
        closes = price_data['close']
        return {
            'sma_20': float(closes.rolling(20).mean().iloc[-1]),
            'sma_50': float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else float(closes.mean()),
            'rsi': 50.0,  # 简化
            'macd': 0.0,  # 简化
            'macd_signal': 0.0,  # 简化
            'current_price': float(closes.iloc[-1])
        }

class FundamentalAnalyzer:
    pass  # 需要实际实现

class SentimentAnalyzer:
    pass  # 需要实际实现

class AIAnalyzer:
    def __init__(self, ai_models: List[str]):
        self.ai_models = ai_models
    
    async def analyze(self, symbol: str, market_data: Dict):
        """AI分析 - 简化实现"""
        await asyncio.sleep(0.2)
        
        # 模拟AI分析结果
        return type('obj', (object,), {
            'action': "BUY" if np.random.random() > 0.5 else "SELL",
            'confidence': np.random.uniform(0.6, 0.9),
            'target_price': market_data.get('current_price', 0) * np.random.uniform(0.9, 1.1),
            'stop_loss': market_data.get('current_price', 0) * np.random.uniform(0.85, 0.98),
            'reasoning': f"AI分析建议"
        })()