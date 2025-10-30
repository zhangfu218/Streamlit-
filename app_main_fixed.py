# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import threading
import queue
import sqlite3
import os
import sys
from pathlib import Path
import psutil
import gc

# 添加缺失的类型注解导入
from typing import Dict, List, Any, Optional, Union, Tuple

# 添加自定义模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
try:
    from core.data_manager import DataManager
    from core.ai_engine import AIEngine
    from core.trading_engine import TradingEngine
    from core.risk_manager import RiskManager
    from core.portfolio_manager import PortfolioManager
    from utils.offline_mode import OfflineMode
    from utils.memory_manager import MemoryManager
except ImportError as e:
    st.error(f"模块导入错误: {e}")
    # 创建基础类作为备用
    class DataManager:
        def __init__(self): pass
    class AIEngine:
        def __init__(self): pass
    class TradingEngine:
        def __init__(self): pass
    class RiskManager:
        def __init__(self): pass
    class PortfolioManager:
        def __init__(self): pass
    class OfflineMode:
        def __init__(self): pass
    class MemoryManager:
        def __init__(self): pass

class QuantumAITradingSystem:
    """量子AI交易系统 - 专业版"""
    
    def __init__(self):
        self.setup_page_config()
        self.setup_custom_styles()
        self.setup_session_state()
        self.initialize_system_components()
        self.setup_ai_models()
    
    def setup_page_config(self):
        """页面配置"""
        st.set_page_config(
            page_title="量子AI交易系统 v6.0",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_custom_styles(self):
        """设置专业交易界面样式"""
        st.markdown("""
        <style>
        .main { 
            background-color: #0a0e17; 
            color: #ffffff; 
        }
        .stApp { 
            background: linear-gradient(135deg, #0a0e17 0%, #1a1f2e 100%); 
        }
        .trading-panel {
            background: #1e2536;
            border: 1px solid #2a3246;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }
        .metric-panel {
            background: linear-gradient(135deg, #2a3246 0%, #1e2536 100%);
            border: 1px solid #3a4256;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }
        .data-table {
            background: #1e2536;
            border: 1px solid #2a3246;
            border-radius: 6px;
        }
        .tab-content {
            background: #1e2536;
            padding: 16px;
            border-radius: 6px;
            margin-top: 8px;
        }
        .status-online { color: #00d4aa; font-weight: bold; }
        .status-offline { color: #ff6b6b; font-weight: bold; }
        .status-warning { color: #ffd93d; font-weight: bold; }
        .buy-signal { color: #00d4aa; }
        .sell-signal { color: #ff6b6b; }
        .hold-signal { color: #ffd93d; }
        .ai-model-card {
            background: linear-gradient(135deg, #2a3246 0%, #1e2536 100%);
            border: 1px solid #3a4256;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_session_state(self):
        """初始化会话状态"""
        default_states = {
            # 系统状态
            'system_initialized': False,
            'data_connection': True,
            'offline_mode': False,
            'last_data_update': datetime.now(),
            
            # 用户状态
            'logged_in': False,
            'current_broker': None,
            'trading_mode': 'simulation',  # real, simulation
            'user_account': None,
            
            # AI配置
            'ai_auto_trading': True,
            'ai_takeover_pending': False,
            'ai_models_configured': False,
            'deepseek_key': '',
            'qwen_key': '',
            'openai_key': '',
            'gemini_key': '',
            
            # 数据存储
            'market_data': {},
            'stock_recommendations': [],
            'portfolio_data': {},
            'trading_history': [],
            'ai_analysis_results': {},
            'system_health': {},
            
            # 页面状态
            'current_tab': 'dashboard',
            'selected_stock': '000001',
            'analysis_period': 30,
            
            # 新增状态
            'ai_models_status': {},
            'consensus_analysis': {},
            'memory_usage': {},
            'real_time_data': {},
            'multi_market_data': {}
        }
        
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def initialize_system_components(self):
        """初始化系统组件"""
        if not st.session_state.system_initialized:
            try:
                # 初始化数据管理器
                self.data_manager = DataManager()
                
                # 初始化AI引擎
                self.ai_engine = AIEngine()
                
                # 初始化交易引擎
                self.trading_engine = TradingEngine()
                
                # 初始化风险管理器
                self.risk_manager = RiskManager()
                
                # 初始化组合管理器
                self.portfolio_manager = PortfolioManager()
                
                # 初始化离线模式
                self.offline_mode = OfflineMode()
                
                # 初始化内存管理器
                self.memory_manager = MemoryManager()
                
                # 启动数据更新线程
                self.start_data_update_thread()
                
                # 启动内存监控线程
                self.start_memory_monitor_thread()
                
                st.session_state.system_initialized = True
                st.session_state.system_health = self.get_system_health()
                
            except Exception as e:
                st.error(f"系统初始化失败: {str(e)}")
                # 启用离线模式
                st.session_state.offline_mode = True
                st.session_state.system_initialized = True
    
    def setup_ai_models(self):
        """设置四大AI模型"""
        self.ai_models = {
            'deepseek': {
                'name': 'DeepSeek',
                'api_key': st.session_state.deepseek_key,
                'enabled': bool(st.session_state.deepseek_key),
                'status': '在线' if st.session_state.deepseek_key else '未配置'
            },
            'qwen': {
                'name': '通义千问', 
                'api_key': st.session_state.qwen_key,
                'enabled': bool(st.session_state.qwen_key),
                'status': '在线' if st.session_state.qwen_key else '未配置'
            },
            'openai': {
                'name': 'ChatGPT',
                'api_key': st.session_state.openai_key,
                'enabled': bool(st.session_state.openai_key),
                'status': '在线' if st.session_state.openai_key else '未配置'
            },
            'gemini': {
                'name': 'Gemini',
                'api_key': st.session_state.gemini_key,
                'enabled': bool(st.session_state.gemini_key),
                'status': '在线' if st.session_state.gemini_key else '未配置'
            }
        }
    
    def start_data_update_thread(self):
        """启动数据更新线程"""
        def data_update_worker():
            while True:
                try:
                    if not st.session_state.offline_mode:
                        # 更新市场数据
                        self.update_market_data()
                        # 更新AI分析
                        self.update_ai_analysis()
                        # 更新系统健康状态
                        st.session_state.system_health = self.get_system_health()
                        # 更新内存使用情况
                        if hasattr(self, 'memory_manager'):
                            st.session_state.memory_usage = self.memory_manager.get_memory_usage()
                    
                    time.sleep(60)  # 每分钟更新一次
                    
                except Exception as e:
                    print(f"数据更新错误: {e}")
                    st.session_state.offline_mode = True
                    time.sleep(30)  # 错误时稍后重试
        
        thread = threading.Thread(target=data_update_worker, daemon=True)
        thread.start()
    
    def start_memory_monitor_thread(self):
        """启动内存监控线程"""
        def memory_monitor_worker():
            while True:
                try:
                    # 检查内存使用情况
                    if hasattr(self, 'memory_manager'):
                        memory_info = self.memory_manager.get_memory_usage()
                        st.session_state.memory_usage = memory_info
                    
                    time.sleep(30)  # 每30秒检查一次
                    
                except Exception as e:
                    print(f"内存监控错误: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=memory_monitor_worker, daemon=True)
        thread.start()
    
    def update_market_data(self):
        """更新市场数据"""
        try:
            # 这里集成真实数据源
            # 模拟数据更新
            st.session_state.market_data = self.get_sample_market_data()
            st.session_state.multi_market_data = self.get_multi_market_data()
            st.session_state.last_data_update = datetime.now()
            
        except Exception as e:
            st.session_state.offline_mode = True
            # 切换到离线数据
            if hasattr(self, 'offline_mode'):
                st.session_state.market_data = self.offline_mode.get_market_data('A股', 'indices')
    
    def update_ai_analysis(self):
        """更新AI分析"""
        try:
            # 获取AI分析结果
            recommendations = self.generate_ai_recommendations()
            st.session_state.stock_recommendations = recommendations
            
            # 更新个股分析
            if st.session_state.selected_stock:
                analysis = self.get_ai_stock_analysis(st.session_state.selected_stock)
                st.session_state.ai_analysis_results[st.session_state.selected_stock] = analysis
                
                # 更新共识分析
                consensus = self.get_ai_consensus_analysis(st.session_state.selected_stock)
                st.session_state.consensus_analysis[st.session_state.selected_stock] = consensus
                
        except Exception as e:
            print(f"AI分析更新失败: {e}")
            # 使用离线分析
            if st.session_state.selected_stock and hasattr(self, 'offline_mode'):
                offline_analysis = self.offline_mode.get_ai_analysis('deepseek', st.session_state.selected_stock, 'technical')
                st.session_state.ai_analysis_results[st.session_state.selected_stock] = offline_analysis
    
    def get_multi_market_data(self):
        """获取多市场数据"""
        return {
            'A股': {
                '上证指数': {'value': 3250.12, 'change': +1.23},
                '深证成指': {'value': 11500.45, 'change': +0.89},
                '创业板指': {'value': 2350.67, 'change': +2.15}
            },
            '港股': {
                '恒生指数': {'value': 18500.23, 'change': -0.45},
                '国企指数': {'value': 6250.67, 'change': -0.23}
            },
            '美股': {
                '道琼斯': {'value': 34567.89, 'change': +0.67},
                '纳斯达克': {'value': 13789.01, 'change': +1.23},
                '标普500': {'value': 4456.78, 'change': +0.89}
            }
        }
    
    def get_ai_consensus_analysis(self, symbol: str) -> Dict[str, Any]:
        """获取四大AI模型共识分析"""
        analyses = {}
        
        for model_id, model_info in self.ai_models.items():
            if model_info['enabled']:
                try:
                    analysis = self.get_single_model_analysis(model_id, symbol)
                    analyses[model_id] = analysis
                except Exception as e:
                    print(f"{model_info['name']}分析失败: {e}")
                    # 使用离线分析作为备选
                    if hasattr(self, 'offline_mode'):
                        offline_analysis = self.offline_mode.get_ai_analysis(model_id, symbol, 'technical')
                        analyses[model_id] = offline_analysis
        
        return self.calculate_consensus(analyses)
    
    def calculate_consensus(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """计算模型共识"""
        if not analyses:
            return {
                'consensus_recommendation': '持有',
                'recommendation_distribution': {'强力买入': 0, '买入': 0, '持有': 1, '减持': 0, '卖出': 0},
                'average_target_price': 0,
                'average_confidence': 0,
                'model_count': 0,
                'individual_analyses': {}
            }
        
        # 统计推荐分布
        recommendations = {'强力买入': 0, '买入': 0, '持有': 0, '减持': 0, '卖出': 0}
        target_prices = []
        confidences = []
        
        for model_id, analysis in analyses.items():
            rec = analysis.get('recommendation', '持有')
            for key in recommendations:
                if key in rec:
                    recommendations[key] += 1
                    break
            
            target_prices.append(analysis.get('target_price', 0))
            confidences.append(analysis.get('confidence', 0))
        
        # 计算共识
        max_votes = max(recommendations.values())
        consensus_rec = [k for k, v in recommendations.items() if v == max_votes][0]
        
        return {
            'consensus_recommendation': consensus_rec,
            'recommendation_distribution': recommendations,
            'average_target_price': np.mean(target_prices) if target_prices else 0,
            'average_confidence': np.mean(confidences) if confidences else 0,
            'model_count': len(analyses),
            'individual_analyses': analyses
        }
    
    def get_single_model_analysis(self, model_id: str, symbol: str) -> Dict[str, Any]:
        """获取单个模型分析结果"""
        # 这里调用实际的AI引擎
        # 暂时返回模拟数据
        return {
            'recommendation': np.random.choice(['强力买入', '买入', '持有', '减持', '卖出']),
            'target_price': np.random.uniform(5, 200),
            'confidence': np.random.uniform(0.6, 0.95),
            'reasoning': f"{self.ai_models[model_id]['name']}分析: 基于技术面和基本面分析",
            'risk_level': np.random.choice(['低', '中', '高']),
            'position_suggestion': f"{np.random.randint(5, 20)}%",
            'timeframe': f"{np.random.randint(30, 180)}天"
        }

    # 这里只包含了关键修复部分，其余方法保持不变...
    # 实际使用时需要将完整代码的其余部分复制过来

    def run(self):
        """运行应用"""
        try:
            self.render_main_interface()
        except Exception as e:
            st.error(f"系统运行异常: {str(e)}")
            st.info("请尝试刷新页面或联系技术支持")

# 创建应用实例并运行
if __name__ == "__main__":
    try:
        app = QuantumAITradingSystem()
        app.run()
    except Exception as e:
        st.error(f"系统启动失败: {str(e)}")
        st.info("请检查系统配置")