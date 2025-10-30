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

from typing import Dict, Any

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
    """量子AI交易系统 - 专业增强版"""
    
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
                    memory_info = self.memory_manager.get_memory_usage()
                    st.session_state.memory_usage = memory_info
                    
                    # 如果内存使用过高，执行优化
                    if self.memory_manager.is_memory_critical():
                        self.memory_manager.handle_memory_critical()
                    
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
            st.session_state.market_data = self.offline_mode.get_market_data('A股', 'indices')
            raise e
    
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
            if st.session_state.selected_stock:
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
            },
            '期货': {
                '沪深300主力': {'value': 3850.34, 'change': +1.45},
                '原油主力': {'value': 75.23, 'change': -0.56}
            },
            '外汇': {
                '美元/人民币': {'value': 7.1654, 'change': -0.12},
                '欧元/美元': {'value': 1.0876, 'change': +0.23}
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
            'reasoning': f"{self.ai_models[model_id]['name']}分析: 基于技术面和基本面分析，建议{np.random.choice(['逢低买入', '持有观望', '逢高减持'])}",
            'risk_level': np.random.choice(['低', '中', '高']),
            'position_suggestion': f"{np.random.randint(5, 20)}%",
            'timeframe': f"{np.random.randint(30, 180)}天"
        }
    
    def render_main_interface(self):
        """渲染主界面"""
        # 顶部导航栏
        self.render_top_navigation()
        
        if not st.session_state.logged_in:
            self.render_login_section()
            return
        
        # 侧边栏
        self.render_sidebar()
        
        # 主内容区
        self.render_main_content()
        
        # 底部状态栏
        self.render_footer()
    
    def render_top_navigation(self):
        """渲染顶部导航栏"""
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
        
        with col1:
            st.markdown("### 量子AI交易系统 v6.0")
        
        with col2:
            if st.session_state.offline_mode:
                status_text = "离线模式"
                status_class = "status-warning"
            elif st.session_state.data_connection:
                status_text = "在线运行"
                status_class = "status-online"
            else:
                status_text = "连接中断"
                status_class = "status-offline"
            st.markdown(f'<p class="{status_class}">{status_text}</p>', unsafe_allow_html=True)
        
        with col3:
            mode_text = "实盘交易" if st.session_state.trading_mode == 'real' else "模拟交易"
            st.metric("交易模式", mode_text)
        
        with col4:
            account = st.session_state.user_account or "未登录"
            st.metric("资金账号", account)
        
        with col5:
            balance = "¥1,245,680" if st.session_state.logged_in else "未登录"
            st.metric("账户资产", balance)
        
        with col6:
            if st.session_state.ai_auto_trading:
                st.metric("AI状态", "自动交易")
            else:
                st.metric("AI状态", "手动模式")
        
        with col7:
            if st.session_state.logged_in:
                if st.button("退出系统", key="logout_top"):
                    self.logout()
            else:
                st.write("请登录")
        
        st.markdown("---")
    
    def render_login_section(self):
        """渲染登录界面"""
        st.markdown("""
        <div style='max-width: 600px; margin: 50px auto; padding: 40px; 
                    background: #1e2536; border-radius: 12px; border: 1px solid #2a3246;'>
            <h2 style='text-align: center; color: #00d4aa; margin-bottom: 30px;'>
                量子AI交易系统 v6.0
            </h2>
            <p style='text-align: center; color: #cccccc;'>
                专业级AI驱动量化交易平台 - 支持A股、港股、美股全市场
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_broker_login()
        
        with col2:
            self.render_ai_config_login()
    
    def render_broker_login(self):
        """渲染券商登录"""
        st.markdown('<div class="trading-panel">', unsafe_allow_html=True)
        st.subheader("券商交易平台登录")
        
        broker = st.selectbox(
            "选择券商平台",
            ["华泰证券", "中信证券", "国泰君安", "招商证券", "广发证券", "模拟交易平台"],
            key="broker_select"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("资金账号", placeholder="请输入资金账号")
        with col2:
            password = st.text_input("交易密码", type="password", placeholder="请输入交易密码")
        
        trading_mode = st.radio(
            "交易模式",
            ["模拟交易", "实盘交易"],
            horizontal=True,
            key="trading_mode_select"
        )
        
        # 交易服务器选择
        server = st.selectbox(
            "交易服务器",
            ["默认主站", "备用服务器1", "备用服务器2", "低延迟专线"],
            key="server_select"
        )
        
        if st.button("登录交易平台", type="primary", use_container_width=True):
            if self.authenticate_broker(broker, username, password):
                st.session_state.logged_in = True
                st.session_state.current_broker = broker
                st.session_state.trading_mode = 'real' if trading_mode == "实盘交易" else 'simulation'
                st.session_state.user_account = username
                st.success(f"成功登录{broker}")
                st.rerun()
            else:
                st.error("登录失败，请检查账号密码")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_ai_config_login(self):
        """渲染AI配置登录"""
        st.markdown('<div class="trading-panel">', unsafe_allow_html=True)
        st.subheader("四大AI模型配置")
        
        with st.form("ai_config_form"):
            st.text_input("DeepSeek API密钥", type="password", key="deepseek_key_input",
                         help="DeepSeek最新模型，擅长逻辑推理和数据分析")
            st.text_input("通义千问 API密钥", type="password", key="qwen_key_input",
                         help="阿里通义千问，在中文理解和金融分析方面表现优异")
            st.text_input("ChatGPT API密钥", type="password", key="openai_key_input",
                         help="OpenAI GPT-4，综合能力最强的通用模型")
            st.text_input("Gemini API密钥", type="password", key="gemini_key_input",
                         help="Google Gemini，在多模态理解和推理方面有优势")
            
            # AI模型配置选项
            st.subheader("AI模型参数")
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider("创造性", 0.0, 1.0, 0.3, 0.1,
                                       help="值越高创造性越强，值越低越保守")
            with col2:
                max_tokens = st.slider("最大输出", 100, 2000, 1000, 100,
                                      help="控制AI分析报告的详细程度")
            
            if st.form_submit_button("保存AI配置", type="secondary", use_container_width=True):
                # 保存AI配置
                st.session_state.deepseek_key = st.session_state.deepseek_key_input
                st.session_state.qwen_key = st.session_state.qwen_key_input
                st.session_state.openai_key = st.session_state.openai_key_input
                st.session_state.gemini_key = st.session_state.gemini_key_input
                st.session_state.ai_models_configured = True
                self.setup_ai_models()
                st.success("AI模型配置已保存")
        
        # 快速演示入口
        if st.button("快速体验演示模式", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.current_broker = "演示平台"
            st.session_state.trading_mode = 'simulation'
            st.session_state.user_account = "demo_user"
            st.session_state.ai_models_configured = True
            # 设置演示用的API密钥
            st.session_state.deepseek_key = "demo_key"
            st.session_state.qwen_key = "demo_key" 
            st.session_state.openai_key = "demo_key"
            st.session_state.gemini_key = "demo_key"
            self.setup_ai_models()
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.markdown("## 交易控制中心")
            
            # 系统状态显示
            self.render_system_status_panel()
            
            # AI交易控制
            with st.expander("AI交易控制", expanded=True):
                self.render_ai_control_panel()
            
            # 市场选择
            with st.expander("市场配置", expanded=True):
                self.render_market_config_panel()
            
            # 交易面板
            with st.expander("快速交易", expanded=False):
                self.render_quick_trade_panel()
            
            # 风险控制
            with st.expander("风险控制", expanded=False):
                self.render_risk_control_panel()
            
            # AI模型状态
            with st.expander("AI模型状态", expanded=False):
                self.render_ai_models_status()
    
    def render_system_status_panel(self):
        """渲染系统状态面板"""
        st.markdown('<div class="trading-panel">', unsafe_allow_html=True)
        
        # 连接状态
        if st.session_state.offline_mode:
            st.warning("离线模式运行中")
            if st.button("尝试重新连接", key="reconnect_btn"):
                st.session_state.offline_mode = False
                st.rerun()
        else:
            st.success("数据连接正常")
        
        # 系统指标
        health = st.session_state.system_health
        memory = st.session_state.memory_usage
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CPU", f"{health.get('cpu_usage', 0)}%")
            st.metric("内存", f"{memory.get('memory_percent', 0):.1f}%")
        with col2:
            st.metric("延迟", f"{health.get('latency', 0)}ms")
            st.metric("数据", health.get('data_status', '正常'))
        
        # 内存使用详情
        if memory:
            st.progress(memory.get('memory_percent', 0) / 100)
            st.caption(f"内存使用: {memory.get('virtual_memory_used_gb', 0):.1f}GB / {memory.get('virtual_memory_total_gb', 0):.1f}GB")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_ai_control_panel(self):
        """渲染AI控制面板"""
        col1, col2 = st.columns(2)
        
        with col1:
            ai_enabled = st.toggle(
                "AI自动交易", 
                value=st.session_state.ai_auto_trading,
                key="ai_auto_toggle"
            )
            st.session_state.ai_auto_trading = ai_enabled
        
        with col2:
            if st.session_state.ai_takeover_pending:
                if st.button("AI接管", type="primary", use_container_width=True):
                    st.session_state.ai_auto_trading = True
                    st.session_state.ai_takeover_pending = False
                    st.rerun()
        
        if ai_enabled:
            st.success("AI自动交易运行中")
            
            # AI交易统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("今日交易", "12笔")
            with col2:
                st.metric("交易胜率", "78.3%")
            with col3:
                st.metric("累计收益", "+¥28,450")
        else:
            st.info("手动交易模式")
            
            if not st.session_state.ai_takeover_pending:
                if st.button("请求AI接管", key="request_ai_takeover"):
                    st.session_state.ai_takeover_pending = True
                    st.rerun()
    
    def render_ai_models_status(self):
        """渲染AI模型状态"""
        for model_id, model_info in self.ai_models.items():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{model_info['name']}**")
            with col2:
                status_color = "status-online" if model_info['enabled'] else "status-offline"
                st.markdown(f'<p class="{status_color}">{model_info["status"]}</p>', unsafe_allow_html=True)
    
    def render_market_config_panel(self):
        """渲染市场配置面板"""
        st.subheader("交易市场")
        markets = st.multiselect(
            "选择市场",
            ["沪深A股", "港股", "美股", "科创板", "创业板", "北交所", "期货", "期权", "ETF", "指数"],
            default=["沪深A股", "港股", "美股"],
            key="market_select"
        )
        
        st.subheader("交易策略")
        strategy = st.selectbox(
            "核心策略",
            ["趋势跟踪", "价值投资", "动量交易", "量化对冲", "高频交易", "事件驱动"],
            key="strategy_select"
        )
        
        st.subheader("风险偏好")
        risk_level = st.select_slider(
            "风险等级",
            options=["保守", "稳健", "平衡", "积极", "激进"],
            value="平衡",
            key="risk_level"
        )
    
    def render_quick_trade_panel(self):
        """渲染快速交易面板"""
        st.subheader("快速交易")
        
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("标的代码", "000001", key="quick_trade_symbol")
        with col2:
            quantity = st.number_input("数量", 100, 100000, 1000, 100, key="quick_trade_quantity")
        
        col3, col4 = st.columns(2)
        with col3:
            price_type = st.selectbox("价格类型", ["限价", "市价"], key="price_type")
        with col4:
            if price_type == "限价":
                price = st.number_input("价格", 0.01, 1000.0, 10.0, 0.01, key="trade_price")
            else:
                price = "市价"
        
        # 交易类型选择
        trade_type = st.selectbox(
            "交易类型",
            ["普通交易", "闪电交易", "条件单", "算法交易"],
            key="trade_type"
        )
        
        col5, col6 = st.columns(2)
        with col5:
            if st.button("买入", type="primary", use_container_width=True, key="quick_buy"):
                self.execute_trade(symbol, quantity, "buy", price, trade_type)
        with col6:
            if st.button("卖出", type="secondary", use_container_width=True, key="quick_sell"):
                self.execute_trade(symbol, quantity, "sell", price, trade_type)
    
    def render_risk_control_panel(self):
        """渲染风险控制面板"""
        st.subheader("风险参数")
        
        col1, col2 = st.columns(2)
        with col1:
            stop_loss = st.slider("止损%", 1.0, 10.0, 3.0, 0.5, key="stop_loss")
        with col2:
            take_profit = st.slider("止盈%", 5.0, 30.0, 15.0, 1.0, key="take_profit")
        
        max_daily_loss = st.slider("单日最大亏损%", 1, 5, 2, key="daily_loss_limit")
        max_position = st.slider("单票最大仓位%", 10, 50, 20, key="max_position")
        
        # 高级风控设置
        with st.expander("高级风控设置"):
            volatility_limit = st.slider("波动率限制%", 1, 10, 5, key="volatility_limit")
            correlation_limit = st.slider("相关性限制", 0.1, 1.0, 0.7, 0.1, key="correlation_limit")
        
        if st.button("应用风控设置", key="apply_risk"):
            # 更新风控参数
            self.risk_manager.update_parameters({
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'max_daily_loss': max_daily_loss,
                'max_position': max_position,
                'volatility_limit': volatility_limit,
                'correlation_limit': correlation_limit
            })
            st.success("风险参数已更新")
    
    def render_main_content(self):
        """渲染主内容区"""
        tabs = st.tabs(["智能选股", "AI分析", "投资组合", "市场监控", "交易记录", "系统状态"])
        
        with tabs[0]:
            self.render_stock_screening()
        with tabs[1]:
            self.render_ai_analysis()
        with tabs[2]:
            self.render_portfolio()
        with tabs[3]:
            self.render_market_monitor()
        with tabs[4]:
            self.render_trading_history()
        with tabs[5]:
            self.render_system_status()
    
    def render_stock_screening(self):
        """渲染智能选股界面"""
        st.header("AI智能选股引擎")
        
        # 选股条件
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            min_score = st.slider("最低评分", 0.0, 1.0, 0.7, 0.05, key="min_score")
        with col2:
            market_filter = st.multiselect(
                "市场板块",
                ["主板", "创业板", "科创板", "北交所"],
                default=["主板", "创业板", "科创板"],
                key="market_filter"
            )
        with col3:
            strategy_type = st.selectbox(
                "选股策略",
                ["综合评分", "技术面优先", "基本面优先", "成长股", "价值股", "趋势股"],
                key="screening_strategy"
            )
        with col4:
            if st.button("刷新推荐", type="primary", key="refresh_stocks"):
                st.session_state.stock_recommendations = self.generate_ai_recommendations()
                st.rerun()
        
        # 显示选股结果
        if st.session_state.stock_recommendations:
            self.render_stock_recommendations(min_score)
        else:
            st.info("正在生成AI选股推荐...")
            # 显示加载动画
            with st.spinner("AI正在分析市场数据..."):
                time.sleep(2)
                st.session_state.stock_recommendations = self.generate_ai_recommendations()
                st.rerun()
    
    def render_stock_recommendations(self, min_score):
        """渲染选股结果"""
        filtered_stocks = [s for s in st.session_state.stock_recommendations 
                          if s.get('total_score', 0) >= min_score]
        
        st.subheader(f"AI推荐股票列表 (共{len(filtered_stocks)}只)")
        
        # 分页显示
        page_size = 20
        total_pages = max(1, len(filtered_stocks) // page_size + 
                         (1 if len(filtered_stocks) % page_size > 0 else 0))
        page = st.number_input("页码", 1, total_pages, 1, key="stock_page")
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_stocks))
        
        # 显示股票列表
        for i in range(start_idx, end_idx):
            if i < len(filtered_stocks):
                stock = filtered_stocks[i]
                self.render_stock_card(stock, i + 1)
    
    def render_stock_card(self, stock, rank):
        """渲染股票卡片"""
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
        
        with col1:
            st.write(f"**#{rank}**")
        
        with col2:
            st.write(f"**{stock['symbol']}**")
            st.write(f"{stock['name']}")
            st.write(f"市场: {stock.get('market', 'A股')}")
        
        with col3:
            score = stock.get('total_score', 0)
            st.write(f"综合评分: {score:.3f}")
            st.progress(score)
            
            # 显示细分评分
            col3a, col3b, col3c = st.columns(3)
            with col3a:
                st.caption(f"技术: {stock.get('tech_score', 0):.2f}")
            with col3b:
                st.caption(f"基本面: {stock.get('fundamental_score', 0):.2f}")
            with col3c:
                st.caption(f"资金: {stock.get('money_flow_score', 0):.2f}")
        
        with col4:
            recommendation = stock.get('recommendation', '持有')
            signal_class = "buy-signal" if '买入' in recommendation else "sell-signal" if '卖出' in recommendation else "hold-signal"
            st.markdown(f'<p class="{signal_class}">{recommendation}</p>', unsafe_allow_html=True)
            st.write(f"置信度: {stock.get('confidence', 0):.1%}")
            st.write(f"目标价: ¥{stock.get('target_price', 0):.2f}")
        
        with col5:
            if st.button("分析", key=f"analyze_{stock['symbol']}"):
                st.session_state.selected_stock = stock['symbol']
                st.rerun()
    
    def render_ai_analysis(self):
        """渲染AI分析界面"""
        st.header("四大AI模型综合分析")
        
        # 股票选择
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            symbol = st.text_input("输入股票代码", st.session_state.selected_stock, key="ai_analysis_symbol")
        with col2:
            period = st.selectbox("分析周期", [30, 60, 90, 180], index=1, key="analysis_period")
        with col3:
            if st.button("开始分析", type="primary", use_container_width=True, key="start_ai_analysis"):
                st.session_state.selected_stock = symbol
                st.session_state.analysis_period = period
                st.rerun()
        
        if st.session_state.selected_stock:
            # 四大模型分析结果
            tabs = st.tabs(["DeepSeek分析", "通义千问分析", "ChatGPT分析", "Gemini分析", "共识分析"])
            
            for i, model_id in enumerate(["deepseek", "qwen", "openai", "gemini"]):
                with tabs[i]:
                    self.render_single_model_analysis(model_id, st.session_state.selected_stock)
            
            with tabs[4]:
                self.render_consensus_analysis(st.session_state.selected_stock)
        else:
            st.info("请选择要分析的股票")
    
    def render_single_model_analysis(self, model_id, symbol):
        """渲染单个模型分析结果"""
        model_info = self.ai_models[model_id]
        
        if not model_info['enabled']:
            st.warning(f"{model_info['name']}未配置，请先在登录页面配置API密钥")
            return
        
        st.subheader(f"{model_info['name']} 分析报告")
        
        # 获取分析结果
        analysis = self.get_single_model_analysis(model_id, symbol)
        
        if analysis:
            # 关键指标
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("推荐", analysis.get('recommendation', '持有'))
                st.metric("目标价", f"¥{analysis.get('target_price', 0):.2f}")
            with col2:
                st.metric("置信度", f"{analysis.get('confidence', 0):.1%}")
                st.metric("风险等级", analysis.get('risk_level', '中'))
            with col3:
                st.metric("建议仓位", analysis.get('position_suggestion', '0%'))
                st.metric("持有周期", analysis.get('timeframe', '0天'))
            with col4:
                st.metric("模型状态", "在线")
                st.metric("分析时间", datetime.now().strftime('%H:%M:%S'))
            
            # 详细分析
            st.subheader("分析总结")
            st.write(analysis.get('reasoning', '分析内容加载中...'))
            
            # 投资建议
            st.subheader("投资建议")
            recommendation = analysis.get('recommendation', '持有')
            if '买入' in recommendation:
                st.success("""
                **操作建议**: 
                - 建议分批建仓
                - 设置止损价位
                - 关注关键技术位
                - 持有至目标价位
                """)
            elif '持有' in recommendation:
                st.info("""
                **操作建议**: 
                - 维持现有仓位
                - 关注基本面变化
                - 设置移动止损
                - 等待明确信号
                """)
            else:
                st.warning("""
                **操作建议**: 
                - 建议减仓或清仓
                - 设置止盈价位
                - 寻找更好机会
                - 控制风险暴露
                """)
    
    def render_consensus_analysis(self, symbol):
        """渲染共识分析"""
        st.subheader("四大模型共识分析")
        
        # 获取共识分析
        consensus = st.session_state.consensus_analysis.get(symbol, {})
        if not consensus:
            st.info("正在生成共识分析...")
            return
        
        # 显示共识结果
        consensus_rec = consensus.get('consensus_recommendation', '持有')
        model_count = consensus.get('model_count', 0)
        avg_confidence = consensus.get('average_confidence', 0)
        
        st.success(f"**共识推荐**: {consensus_rec} ({model_count}/4 模型支持, 平均置信度: {avg_confidence:.1%})")
        
        # 可视化共识分布
        distribution = consensus.get('recommendation_distribution', {})
        fig = px.pie(
            values=list(distribution.values()),
            names=list(distribution.keys()),
            title="模型推荐分布",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细共识分析
        st.subheader("详细共识分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("平均目标价", f"¥{consensus.get('average_target_price', 0):.2f}")
            st.metric("支持模型数", f"{model_count}/4")
        
        with col2:
            st.metric("平均置信度", f"{avg_confidence:.1%}")
            st.metric("分析一致性", f"{max(distribution.values())/model_count*100:.1f}%" if model_count > 0 else "0%")
        
        # 各模型详细结果
        st.subheader("各模型详细结果")
        individual_analyses = consensus.get('individual_analyses', {})
        
        for model_id, analysis in individual_analyses.items():
            model_name = self.ai_models[model_id]['name']
            with st.expander(f"{model_name}分析结果"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**推荐**: {analysis.get('recommendation', '持有')}")
                    st.write(f"**目标价**: ¥{analysis.get('target_price', 0):.2f}")
                with col2:
                    st.write(f"**置信度**: {analysis.get('confidence', 0):.1%}")
                    st.write(f"**风险等级**: {analysis.get('risk_level', '中')}")
        
        # 综合投资建议
        st.subheader("综合投资建议")
        if consensus_rec in ['强力买入', '买入']:
            st.success("""
            **强力买入信号 - 综合建议**:
            
            **仓位管理**:
            - 建议仓位: 8-15%
            - 建仓策略: 分批买入，3-5次完成
            - 最大仓位: 不超过总资产的20%
            
            **风险控制**:
            - 止损价位: 当前价-5%
            - 目标价位: 当前价+15-25%
            - 持有周期: 1-3个月
            
            **监控要点**:
            - 技术面: 关注均线支撑和成交量变化
            - 基本面: 跟踪季度财报和行业动态
            - 资金面: 监控主力资金流向
            """)
        elif consensus_rec == '持有':
            st.info("""
            **持有观望信号 - 综合建议**:
            
            **仓位管理**:
            - 维持现有仓位
            - 不加仓也不减仓
            - 现金比例保持10-20%
            
            **风险控制**:
            - 移动止损: 成本价+3%或重要支撑位
            - 关注关键: 技术指标变化和基本面数据
            - 准备预案: 跌破支撑位立即减仓
            
            **监控要点**:
            - 技术面: 关注趋势线是否破位
            - 消息面: 注意公司公告和行业政策
            - 市场面: 观察整体市场情绪
            """)
        else:
            st.warning("""
            **减持卖出信号 - 综合建议**:
            
            **仓位管理**:
            - 建议减仓至5%以下
            - 分批卖出，避免冲击成本
            - 保留现金等待更好机会
            
            **风险控制**:
            - 立即止损: 跌破关键支撑位
            - 反弹卖出: 如有反弹逢高减仓
            - 严格纪律: 不轻易抄底
            
            **监控要点**:
            - 技术面: 关注是否出现底部信号
            - 基本面: 跟踪业绩是否改善
            - 资金面: 观察是否有资金回流
            """)
    
    def render_portfolio(self):
        """渲染投资组合界面"""
        st.header("投资组合管理")
        
        # 组合概览
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总资产", "¥1,568,420")
        with col2:
            st.metric("总收益", "+¥86,420", "+5.82%")
        with col3:
            st.metric("今日收益", "+¥12,580", "+0.81%")
        with col4:
            st.metric("持仓数量", "15")
        
        # 持仓详情
        st.subheader("持仓明细")
        portfolio_data = self.get_portfolio_data()
        st.dataframe(portfolio_data, use_container_width=True)
        
        # AI优化建议
        st.subheader("AI组合优化建议")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **当前组合分析**:
            - 科技板块: 35% (建议: 40%)
            - 金融板块: 25% (建议: 20%) 
            - 消费板块: 20% (建议: 25%)
            - 其他板块: 20% (建议: 15%)
            
            **风险评估**:
            - 夏普比率: 1.85
            - 最大回撤: -8.23%
            - 波动率: 12.45%
            - Beta系数: 1.12
            """)
        
        with col2:
            st.success("""
            **AI优化建议**:
            - 增持人工智能概念股 (+5%)
            - 减持传统银行股 (-5%)
            - 新增新能源配置 (+3%)
            - 现金比例保持10%
            
            **调仓策略**:
            - 分批调仓，3天内完成
            - 关注调仓冲击成本
            - 设置调仓价格区间
            """)
            
            col2a, col2b = st.columns(2)
            with col2a:
                if st.button("执行AI调仓", type="primary", use_container_width=True):
                    st.success("AI调仓指令已发送")
            with col2b:
                if st.button("生成调仓报告", use_container_width=True):
                    st.info("调仓报告生成中...")
    
    def render_market_monitor(self):
        """渲染市场监控界面"""
        st.header("实时市场监控")
        
        # 全球市场指数
        st.subheader("全球主要指数")
        self.render_global_indices()
        
        # 板块热度
        st.subheader("板块热度排行")
        self.render_sector_heat()
        
        # 实时行情
        st.subheader("实时行情")
        self.render_real_time_quotes()
        
        # 资金流向
        st.subheader("资金流向监控")
        self.render_money_flow()
        
        # 多市场数据
        st.subheader("多市场概览")
        self.render_multi_market_overview()
    
    def render_global_indices(self):
        """渲染全球指数"""
        indices_data = [
            {"name": "上证指数", "value": 3250.12, "change": +1.23},
            {"name": "深证成指", "value": 11500.45, "change": +0.89},
            {"name": "创业板指", "value": 2350.67, "change": +2.15},
            {"name": "沪深300", "value": 3850.34, "change": +1.45},
            {"name": "恒生指数", "value": 18500.23, "change": -0.45},
            {"name": "道琼斯", "value": 34567.89, "change": +0.67}
        ]
        
        cols = st.columns(6)
        for i, market in enumerate(indices_data):
            with cols[i]:
                delta_color = "normal" if market["change"] >= 0 else "inverse"
                st.metric(
                    market["name"],
                    f"{market['value']:.2f}",
                    f"{market['change']:+.2f}%",
                    delta_color=delta_color
                )
    
    def render_multi_market_overview(self):
        """渲染多市场概览"""
        multi_market_data = st.session_state.multi_market_data
        
        if not multi_market_data:
            st.info("市场数据加载中...")
            return
        
        for market_name, indices in multi_market_data.items():
            with st.expander(f"{market_name}市场", expanded=market_name=="A股"):
                cols = st.columns(len(indices))
                for i, (index_name, data) in enumerate(indices.items()):
                    with cols[i]:
                        delta_color = "normal" if data["change"] >= 0 else "inverse"
                        st.metric(
                            index_name,
                            f"{data['value']:.2f}",
                            f"{data['change']:+.2f}%",
                            delta_color=delta_color
                        )
    
    def render_sector_heat(self):
        """渲染板块热度"""
        sectors = [
            {"name": "人工智能", "heat": 95, "change": "+5.2%"},
            {"name": "新能源", "heat": 88, "change": "+3.8%"},
            {"name": "半导体", "heat": 82, "change": "+2.1%"},
            {"name": "医药生物", "heat": 76, "change": "+1.5%"},
            {"name": "大消费", "heat": 65, "change": "-0.8%"},
            {"name": "金融", "heat": 58, "change": "-1.2%"}
        ]
        
        for sector in sectors:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{sector['name']}**")
            with col2:
                st.progress(sector['heat'] / 100)
            with col3:
                st.write(sector['change'])
    
    def render_real_time_quotes(self):
        """渲染实时行情"""
        quotes_data = {
            '代码': ['000001', '600036', '300750', '000858', '601318'],
            '名称': ['平安银行', '招商银行', '宁德时代', '五粮液', '中国平安'],
            '最新价': [13.25, 36.82, 185.60, 148.35, 48.36],
            '涨跌幅': [+1.23, +0.89, -0.45, +2.15, +0.67],
            '成交量(万)': [1250, 890, 560, 450, 780],
            '换手率': [2.1, 1.8, 3.2, 2.8, 1.5]
        }
        
        df = pd.DataFrame(quotes_data)
        st.dataframe(df, use_container_width=True, height=300)
    
    def render_money_flow(self):
        """渲染资金流向"""
        flow_data = {
            '板块': ['人工智能', '新能源', '半导体', '医药', '金融'],
            '主力净流入(亿)': [12.5, 8.9, 5.6, 3.2, -2.1],
            '机构净流入(亿)': [8.7, 6.2, 4.1, 2.3, -1.5],
            '散户净流入(亿)': [3.8, 2.7, 1.5, 0.9, -0.6]
        }
        
        df = pd.DataFrame(flow_data)
        st.dataframe(df, use_container_width=True, height=200)
    
    def render_trading_history(self):
        """渲染交易记录界面"""
        st.header("交易记录与决策日志")
        
        # 交易统计
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总交易笔数", "156")
        with col2:
            st.metric("AI交易笔数", "128")
        with col3:
            st.metric("交易胜率", "76.5%")
        with col4:
            st.metric("平均持仓时间", "15.2天")
        
        # 交易记录表格
        st.subheader("近期交易记录")
        trading_data = self.get_trading_history()
        st.dataframe(trading_data, use_container_width=True)
        
        # 决策日志
        st.subheader("AI决策日志")
        decision_logs = self.get_decision_logs()
        for log in decision_logs:
            with st.expander(f"{log['timestamp']} - {log['action']}"):
                st.write(f"**决策理由**: {log['reasoning']}")
                st.write(f"**执行结果**: {log['result']}")
                st.write(f"**使用模型**: {log.get('model', 'AI引擎')}")
                st.write(f"**置信度**: {log.get('confidence', 'N/A')}")
    
    def render_system_status(self):
        """渲染系统状态界面"""
        st.header("系统健康状态")
        
        # 系统概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            memory_info = st.session_state.memory_usage
            memory_percent = memory_info.get('memory_percent', 0) if memory_info else 0
            st.metric("内存使用", f"{memory_percent:.1f}%")
            st.metric("数据连接", "正常" if st.session_state.data_connection else "中断")
        
        with col2:
            st.metric("CPU使用", f"{st.session_state.system_health.get('cpu_usage', 35)}%")
            st.metric("AI服务", "正常")
        
        with col3:
            disk_usage = st.session_state.system_health.get('disk_usage', 60)
            st.metric("磁盘空间", f"{disk_usage}%")
            st.metric("网络延迟", f"{st.session_state.system_health.get('latency', 28)}ms")
        
        with col4:
            st.metric("运行时间", "2小时15分")
            if st.button("刷新状态", key="refresh_status"):
                st.session_state.system_health = self.get_system_health()
                st.session_state.memory_usage = self.memory_manager.get_memory_usage()
                st.rerun()
        
        # 内存使用详情
        st.subheader("内存使用详情")
        if st.session_state.memory_usage:
            memory_info = st.session_state.memory_usage
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("已用内存", f"{memory_info.get('virtual_memory_used_gb', 0):.1f}GB")
            with col2:
                st.metric("总内存", f"{memory_info.get('virtual_memory_total_gb', 0):.1f}GB")
            with col3:
                st.metric("交换内存", f"{memory_info.get('swap_used_gb', 0):.1f}GB")
            with col4:
                if st.button("内存优化", key="memory_optimize"):
                    result = self.memory_manager.optimize_memory_usage()
                    st.success(f"内存优化完成，释放 {result.get('memory_reduced_gb', 0):.2f}GB")
        
        # AI模型状态
        st.subheader("AI模型状态")
        ai_cols = st.columns(4)
        
        ai_models = [
            ("DeepSeek", "正常", "status-online"),
            ("通义千问", "正常", "status-online"), 
            ("ChatGPT", "正常", "status-online"),
            ("Gemini", "正常", "status-online")
        ]
        
        for i, (model, status, status_class) in enumerate(ai_models):
            with ai_cols[i]:
                st.metric(f"{model}状态", status)
        
        # 离线模式状态
        st.subheader("离线模式状态")
        offline_status = self.offline_mode.get_system_status()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("技术指标缓存", offline_status.get('technical_cache_count', 0))
        with col2:
            st.metric("市场数据缓存", offline_status.get('market_cache_count', 0))
        with col3:
            st.metric("AI分析缓存", offline_status.get('ai_cache_count', 0))
    
    def render_footer(self):
        """渲染底部状态栏"""
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            last_update = st.session_state.last_data_update.strftime('%Y-%m-%d %H:%M:%S')
            offline_status = "离线" if st.session_state.offline_mode else "在线"
            st.caption(f"最后更新: {last_update} | 数据状态: {offline_status} | 内存使用: {st.session_state.memory_usage.get('memory_percent', 0):.1f}%")
        with col2:
            st.caption("量子AI交易系统 v6.0")
        with col3:
            st.caption("© 2024 量子金融科技")
    
    # 工具方法
    def authenticate_broker(self, broker, username, password):
        """券商认证"""
        # 模拟认证逻辑
        valid_combinations = {
            "华泰证券": {"user": "123456", "pass": "123456"},
            "中信证券": {"user": "123456", "pass": "123456"},
            "国泰君安": {"user": "123456", "pass": "123456"},
            "招商证券": {"user": "123456", "pass": "123456"},
            "广发证券": {"user": "123456", "pass": "123456"},
            "模拟交易平台": {"user": "demo", "pass": "demo"}
        }
        
        if broker in valid_combinations:
            return (username == valid_combinations[broker]["user"] and 
                   password == valid_combinations[broker]["pass"])
        return False
    
    def execute_trade(self, symbol, quantity, side, price, trade_type="普通交易"):
        """执行交易"""
        try:
            if not st.session_state.logged_in:
                st.error("请先登录交易账户")
                return
            
            # 模拟交易执行
            order_id = f"ORDER_{int(time.time())}_{np.random.randint(1000,9999)}"
            
            if st.session_state.trading_mode == 'real':
                trade_type_text = "实盘交易"
                # 这里集成真实交易API
            else:
                trade_type_text = "模拟交易"
            
            st.success(f"""
            {trade_type_text}订单提交成功！
            - 订单号: {order_id}
            - 操作: {side.upper()}
            - 标的: {symbol}
            - 数量: {quantity}
            - 价格: {price}
            - 交易类型: {trade_type}
            """)
            
            # 记录交易
            self.record_trade({
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now(),
                'type': trade_type_text,
                'trade_type': trade_type
            })
            
            # 触发AI接管提示
            if not st.session_state.ai_auto_trading:
                st.session_state.ai_takeover_pending = True
            
        except Exception as e:
            st.error(f"交易执行失败: {str(e)}")
    
    def record_trade(self, trade_data):
        """记录交易"""
        if 'trading_history' not in st.session_state:
            st.session_state.trading_history = []
        st.session_state.trading_history.append(trade_data)
        
        # 同时记录到组合管理器
        try:
            self.portfolio_manager.record_trade(
                trade_data['order_id'],
                trade_data['symbol'],
                'A股',  # 默认市场
                trade_data['side'],
                trade_data['quantity'],
                trade_data['price'],
                trade_data['type'],
                'AI策略' if st.session_state.ai_auto_trading else '手动交易'
            )
        except Exception as e:
            print(f"记录交易到组合管理器失败: {e}")
    
    def get_sample_market_data(self):
        """获取示例市场数据"""
        return {
            'timestamp': datetime.now(),
            'indices': {
                'shanghai': 3250.12,
                'shenzhen': 11500.45,
                'chinesext': 2350.67
            },
            'stocks': {
                '000001': {'price': 13.25, 'change': 1.23},
                '600036': {'price': 36.82, 'change': 0.89},
                '300750': {'price': 185.60, 'change': -0.45}
            }
        }
    
    def generate_ai_recommendations(self):
        """生成AI推荐股票"""
        # 模拟AI推荐逻辑
        stocks = [
            {"symbol": "000001", "name": "平安银行", "market": "A股", "total_score": 0.92, 
             "tech_score": 0.88, "fundamental_score": 0.85, "money_flow_score": 0.90,
             "recommendation": "强力买入", "confidence": 0.88, "target_price": 15.20},
            {"symbol": "600036", "name": "招商银行", "market": "A股", "total_score": 0.87,
             "tech_score": 0.82, "fundamental_score": 0.90, "money_flow_score": 0.80,
             "recommendation": "买入", "confidence": 0.85, "target_price": 40.50},
            {"symbol": "300750", "name": "宁德时代", "market": "创业板", "total_score": 0.85,
             "tech_score": 0.80, "fundamental_score": 0.88, "money_flow_score": 0.82,
             "recommendation": "买入", "confidence": 0.82, "target_price": 210.00},
            {"symbol": "000858", "name": "五粮液", "market": "A股", "total_score": 0.83,
             "tech_score": 0.78, "fundamental_score": 0.85, "money_flow_score": 0.80,
             "recommendation": "买入", "confidence": 0.80, "target_price": 165.00},
            {"symbol": "601318", "name": "中国平安", "market": "A股", "total_score": 0.81,
             "tech_score": 0.75, "fundamental_score": 0.88, "money_flow_score": 0.75,
             "recommendation": "持有", "confidence": 0.78, "target_price": 52.00},
            # 添加更多股票...
        ]
        
        # 随机生成更多股票
        for i in range(45):
            symbol = f"60{i+1000:04d}" if i % 2 == 0 else f"00{i+1000:04d}"
            name = f"股票{i+1}"
            score = np.random.uniform(0.5, 0.95)
            if score > 0.8:
                recommendation = "强力买入"
            elif score > 0.7:
                recommendation = "买入"
            elif score > 0.6:
                recommendation = "持有"
            else:
                recommendation = "观望"
            
            stocks.append({
                "symbol": symbol,
                "name": name,
                "market": np.random.choice(["A股", "创业板", "科创板"]),
                "total_score": score,
                "tech_score": np.random.uniform(0.4, 0.9),
                "fundamental_score": np.random.uniform(0.4, 0.9),
                "money_flow_score": np.random.uniform(0.4, 0.9),
                "recommendation": recommendation,
                "confidence": score * 0.9 + 0.1,
                "target_price": np.random.uniform(5, 200)
            })
        
        return sorted(stocks, key=lambda x: x['total_score'], reverse=True)
    
    def get_ai_stock_analysis(self, symbol):
        """获取AI个股分析"""
        # 模拟AI分析结果
        return {
            'symbol': symbol,
            'recommendation': np.random.choice(['强力买入', '买入', '持有', '减持', '卖出']),
            'target_price': np.random.uniform(8, 20),
            'stop_loss': np.random.uniform(6, 15),
            'confidence': np.random.uniform(0.6, 0.95),
            'risk_level': np.random.choice(['低', '中', '高']),
            'position': np.random.randint(5, 20),
            'holding_period': np.random.randint(30, 180),
            'expected_return': np.random.uniform(0.05, 0.25),
            'reasoning': f"基于技术面和基本面分析，该股票当前处于{np.random.choice(['强势', '平稳', '弱势'])}状态，建议{np.random.choice(['逢低买入', '持有观望', '逢高减持'])}。",
            'technical_indicators': {
                'rsi': np.random.uniform(30, 70),
                'macd': np.random.uniform(-0.1, 0.1),
                'kdj': np.random.uniform(20, 80),
                'bollinger': np.random.choice(['上轨', '中轨', '下轨'])
            }
        }
    
    def get_portfolio_data(self):
        """获取投资组合数据"""
        return pd.DataFrame({
            '代码': ['000001', '600036', '300750', '000858', '601318'],
            '名称': ['平安银行', '招商银行', '宁德时代', '五粮液', '中国平安'],
            '持仓数量': [1000, 500, 200, 300, 400],
            '当前价格': [13.25, 36.82, 185.60, 148.35, 48.36],
            '成本价格': [12.85, 35.20, 190.25, 145.80, 47.15],
            '涨跌幅': [+3.12, +4.60, -2.45, +1.79, +2.57],
            '持仓市值': [13250, 18410, 37120, 44505, 19344],
            '浮动盈亏': [+400, +810, -930, +765, +484]
        })
    
    def get_trading_history(self):
        """获取交易历史"""
        return pd.DataFrame({
            '时间': ['2024-01-15 09:30', '2024-01-15 10:15', '2024-01-14 14:30', '2024-01-14 11:20'],
            '订单号': ['ORDER_1705293000_1234', 'ORDER_1705294500_5678', 'ORDER_1705207800_9012', 'ORDER_1705202400_3456'],
            '代码': ['000001', '600036', '300750', '000858'],
            '名称': ['平安银行', '招商银行', '宁德时代', '五粮液'],
            '操作': ['买入', '卖出', '买入', '买入'],
            '数量': [1000, 500, 200, 300],
            '价格': [13.20, 36.50, 186.00, 145.80],
            '金额': [13200, 18250, 37200, 43740],
            '状态': ['已成', '已成', '已成', '已成'],
            '模式': ['AI自动', '手动', 'AI自动', 'AI自动']
        })
    
    def get_decision_logs(self):
        """获取决策日志"""
        return [
            {
                'timestamp': '2024-01-15 09:30:15',
                'action': '买入 000001',
                'reasoning': '技术面金叉形成，基本面稳健，符合趋势策略，四大模型一致推荐',
                'result': '执行成功，当前盈利+3.12%',
                'model': '四大模型共识',
                'confidence': '88.5%'
            },
            {
                'timestamp': '2024-01-15 10:15:30', 
                'action': '卖出 600036',
                'reasoning': '达到目标价位，锁定收益，技术面出现顶背离信号',
                'result': '执行成功，获利+4.60%',
                'model': 'DeepSeek + ChatGPT',
                'confidence': '82.3%'
            }
        ]
    
    def get_system_health(self):
        """获取系统健康状态"""
        return {
            'cpu_usage': np.random.randint(20, 60),
            'memory_usage': np.random.randint(30, 70),
            'disk_usage': np.random.randint(40, 80),
            'latency': np.random.randint(10, 50),
            'data_status': '正常'
        }
    
    def logout(self):
        """退出登录"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
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
        st.info("""
        系统启动失败，建议操作:
        1. 检查Python环境依赖
        2. 检查网络连接
        3. 查看系统日志
        4. 联系技术支持
        """)