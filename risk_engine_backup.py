# risk_engine.py
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RiskAssessment:
    """风险评估结果"""
    is_approved: bool
    risk_level: str  # LOW, MEDIUM, HIGH
    rejection_reason: str = ""
    suggested_adjustments: Dict[str, Any] = None
    max_position_size: float = 0
    confidence_score: float = 0

@dataclass
class PortfolioRisk:
    """投资组合风险"""
    total_value: float
    var_95: float  # 95%置信度的在险价值
    cvar_95: float  # 条件在险价值
    max_drawdown: float
    sharpe_ratio: float
    beta: float

class AIRiskEngine:
    """AI风险引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.position_tracker = PositionTracker()
        self.performance_monitor = PerformanceMonitor()
        self.market_analyzer = MarketAnalyzer()
        
        # 风险参数
        self.risk_params = config.get('risk_params', {
            'max_position_ratio': 0.1,  # 单票最大仓位
            'max_portfolio_risk': 0.3,   # 组合最大风险
            'daily_loss_limit': 0.03,    # 单日最大亏损
            'var_confidence': 0.95,      # VaR置信度
            'max_drawdown_limit': 0.15   # 最大回撤限制
        })
    
    async def validate_trade_signal(self, signal, market_data: Dict) -> RiskAssessment:
        """验证交易信号风险"""
        try:
            checks = [
                await self.check_position_limit(signal, market_data),
                await self.check_daily_loss_limit(),
                await self.check_sector_exposure(signal),
                await self.check_market_condition(),
                await self.check_volatility(signal, market_data),
                await self.check_liquidity(signal, market_data)
            ]
            
            # 计算综合风险评分
            risk_score = sum(1 for check in checks if not check['passed']) / len(checks)
            
            if risk_score >= 0.5:  # 超过50%的检查失败
                return RiskAssessment(
                    is_approved=False,
                    risk_level="HIGH",
                    rejection_reason=f"风险过高，{int(risk_score*100)}%的检查未通过",
                    confidence_score=1 - risk_score
                )
            
            # 计算建议的最大仓位
            max_position = self.calculate_max_position(signal, market_data)
            
            return RiskAssessment(
                is_approved=True,
                risk_level="LOW" if risk_score < 0.2 else "MEDIUM",
                max_position_size=max_position,
                confidence_score=1 - risk_score
            )
            
        except Exception as e:
            return RiskAssessment(
                is_approved=False,
                risk_level="HIGH",
                rejection_reason=f"风险评估错误: {str(e)}",
                confidence_score=0.0
            )
    
    async def check_position_limit(self, signal, market_data: Dict) -> Dict[str, Any]:
        """检查仓位限制"""
        try:
            current_positions = self.position_tracker.get_current_positions()
            portfolio_value = self.position_tracker.get_portfolio_value()
            
            # 计算新交易后的仓位
            if signal.action == "BUY":
                new_position_value = sum(pos['value'] for pos in current_positions) + signal.quantity * market_data.get('current_price', 0)
            else:
                new_position_value = sum(pos['value'] for pos in current_positions)
            
            max_portfolio_value = portfolio_value * (1 + self.risk_params['max_portfolio_risk'])
            
            passed = new_position_value <= max_portfolio_value
            message = "仓位检查通过" if passed else f"仓位超出限制: {new_position_value:.0f} > {max_portfolio_value:.0f}"
            
            return {'passed': passed, 'message': message}
            
        except Exception as e:
            return {'passed': False, 'message': f"仓位检查错误: {str(e)}"}
    
    async def check_daily_loss_limit(self) -> Dict[str, Any]:
        """检查日亏损限制"""
        try:
            daily_pnl = self.performance_monitor.get_daily_pnl()
            daily_limit = self.position_tracker.get_portfolio_value() * self.risk_params['daily_loss_limit']
            
            passed = daily_pnl >= -daily_limit
            message = "日亏损检查通过" if passed else f"日亏损超出限制: {daily_pnl:.0f} < {-daily_limit:.0f}"
            
            return {'passed': passed, 'message': message}
            
        except Exception as e:
            return {'passed': False, 'message': f"日亏损检查错误: {str(e)}"}
    
    async def check_sector_exposure(self, signal) -> Dict[str, Any]:
        """检查行业暴露"""
        try:
            # 这里应该实现行业暴露度检查
            # 简化实现：随机通过
            passed = True  # 简化实现
            message = "行业暴露检查通过"
            
            return {'passed': passed, 'message': message}
            
        except Exception as e:
            return {'passed': False, 'message': f"行业暴露检查错误: {str(e)}"}
    
    async def check_market_condition(self) -> Dict[str, Any]:
        """检查市场状况"""
        try:
            market_condition = await self.market_analyzer.get_market_condition()
            
            # 如果市场处于极端状况，限制交易
            if market_condition.get('volatility', 0) > 0.5:  # 高波动
                return {'passed': False, 'message': "市场波动过高，限制交易"}
            elif market_condition.get('sentiment', 0) < 0.2:  # 极度悲观
                return {'passed': False, 'message': "市场情绪极度悲观，限制交易"}
            else:
                return {'passed': True, 'message': "市场状况良好"}
                
        except Exception as e:
            return {'passed': False, 'message': f"市场状况检查错误: {str(e)}"}
    
    async def check_volatility(self, signal, market_data: Dict) -> Dict[str, Any]:
        """检查波动率"""
        try:
            # 计算历史波动率
            price_data = market_data.get('price_data')
            if price_data is not None and len(price_data) > 20:
                returns = price_data['close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)  # 年化波动率
                
                if volatility > 0.6:  # 60%年化波动率
                    return {'passed': False, 'message': f"波动率过高: {volatility:.1%}"}
                else:
                    return {'passed': True, 'message': f"波动率正常: {volatility:.1%}"}
            else:
                return {'passed': True, 'message': "波动率数据不足，默认通过"}
                
        except Exception as e:
            return {'passed': False, 'message': f"波动率检查错误: {str(e)}"}
    
    async def check_liquidity(self, signal, market_data: Dict) -> Dict[str, Any]:
        """检查流动性"""
        try:
            # 简化实现：检查成交量
            volume = market_data.get('volume', 0)
            required_liquidity = signal.quantity * market_data.get('current_price', 0)
            
            # 假设需要成交金额不超过日均成交额的1%
            if volume > 0 and required_liquidity > volume * 0.01:
                return {'passed': False, 'message': f"流动性不足: 需要{required_liquidity:.0f}，可用{volume*0.01:.0f}"}
            else:
                return {'passed': True, 'message': "流动性充足"}
                
        except Exception as e:
            return {'passed': False, 'message': f"流动性检查错误: {str(e)}"}
    
    def calculate_max_position(self, signal, market_data: Dict) -> float:
        """计算最大允许仓位"""
        portfolio_value = self.position_tracker.get_portfolio_value()
        max_single_position = portfolio_value * self.risk_params['max_position_ratio']
        
        current_price = market_data.get('current_price', 0)
        if current_price > 0:
            max_shares = max_single_position / current_price
            return min(signal.quantity, max_shares)
        else:
            return signal.quantity
    
    async def calculate_portfolio_risk(self) -> PortfolioRisk:
        """计算投资组合风险"""
        try:
            positions = self.position_tracker.get_current_positions()
            historical_data = self.performance_monitor.get_historical_performance()
            
            # 简化实现 - 实际应该使用更复杂的风险模型
            total_value = sum(pos['value'] for pos in positions)
            
            # 模拟风险计算
            var_95 = total_value * 0.05  # 5% VaR
            cvar_95 = total_value * 0.08  # 8% CVaR
            max_drawdown = 0.12  # 12%最大回撤
            sharpe_ratio = 1.5
            beta = 1.1
            
            return PortfolioRisk(
                total_value=total_value,
                var_95=var_95,
                cvar_95=cvar_95,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                beta=beta
            )
            
        except Exception as e:
            # 返回默认值
            return PortfolioRisk(
                total_value=0,
                var_95=0,
                cvar_95=0,
                max_drawdown=0,
                sharpe_ratio=0,
                beta=1.0
            )
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """获取风险指标"""
        try:
            portfolio_risk = asyncio.run(self.calculate_portfolio_risk())
            
            return {
                'portfolio_value': portfolio_risk.total_value,
                'var_95': portfolio_risk.var_95,
                'cvar_95': portfolio_risk.cvar_95,
                'max_drawdown': portfolio_risk.max_drawdown,
                'sharpe_ratio': portfolio_risk.sharpe_ratio,
                'beta': portfolio_risk.beta,
                'position_concentration': self.calculate_position_concentration(),
                'sector_concentration': self.calculate_sector_concentration(),
                'liquidity_risk': self.calculate_liquidity_risk()
            }
            
        except Exception as e:
            return {'error': f"风险指标计算错误: {str(e)}"}
    
    def calculate_position_concentration(self) -> float:
        """计算持仓集中度"""
        positions = self.position_tracker.get_current_positions()
        if not positions:
            return 0.0
        
        total_value = sum(pos['value'] for pos in positions)
        if total_value == 0:
            return 0.0
        
        # 赫芬达尔指数
        concentration = sum((pos['value'] / total_value) ** 2 for pos in positions)
        return concentration
    
    def calculate_sector_concentration(self) -> Dict[str, float]:
        """计算行业集中度"""
        # 简化实现
        return {'technology': 0.4, 'finance': 0.3, 'healthcare': 0.2, 'other': 0.1}
    
    def calculate_liquidity_risk(self) -> float:
        """计算流动性风险"""
        # 简化实现
        return 0.2

# 辅助类（简化实现）
class PositionTracker:
    def get_current_positions(self):
        """获取当前持仓 - 简化实现"""
        return [
            {'symbol': '000001.SZ', 'value': 50000},
            {'symbol': '600036.SH', 'value': 75000},
            {'symbol': '00700.HK', 'value': 100000}
        ]
    
    def get_portfolio_value(self):
        """获取组合价值 - 简化实现"""
        return 500000

class PerformanceMonitor:
    def get_daily_pnl(self):
        """获取当日盈亏 - 简化实现"""
        return 15000
    
    def get_historical_performance(self):
        """获取历史表现 - 简化实现"""
        return pd.DataFrame()

class MarketAnalyzer:
    async def get_market_condition(self):
        """获取市场状况 - 简化实现"""
        return {'volatility': 0.3, 'sentiment': 0.6}