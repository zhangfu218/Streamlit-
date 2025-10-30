import os
from datetime import timedelta

class SystemConfig:
    """系统全局配置"""
    
    # 基础配置
    APP_NAME = "量子智能交易系统"
    VERSION = "3.0.0"
    DEBUG = True
    
    # 路径配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DATABASE_PATH = os.path.join(DATA_DIR, "database", "trading_system.db")
    CACHE_DIR = os.path.join(DATA_DIR, "cache")
    LOG_DIR = os.path.join(DATA_DIR, "logs")
    
    # 内存管理配置
    MEMORY = {
        "max_usage_percent": 0.7,
        "cache_size_limit_mb": 1000,
        "auto_clean_interval": 300,
        "emergency_threshold": 0.85
    }
    
    # 连接配置
    CONNECTION = {
        "timeout": 30,
        "retry_times": 3,
        "retry_interval": 60,
        "offline_mode": False
    }

class TradingConfig:
    """交易配置"""
    
    # 市场配置
    MARKETS = {
        "A股": ["SH", "SZ", "BJ"],
        "港股": ["HK"],
        "美股": ["US"],
        "期货": ["FUTURES"],
        "期权": ["OPTIONS"],
        "ETF": ["ETF"]
    }
    
    # 交易参数
    TRADING = {
        "default_strategies": ["趋势跟踪", "均值回归", "动量策略", "套利策略"],
        "max_position_ratio": 0.1,
        "stop_loss": 0.05,
        "take_profit": 0.15,
        "max_drawdown": 0.1,
        "slippage": 0.001
    }
    
    # 券商接口配置
    BROKERS = {
        "simulation": {
            "name": "模拟交易",
            "enabled": True
        },
        "futu": {
            "name": "富途证券",
            "enabled": False
        },
        "ib": {
            "name": "盈透证券", 
            "enabled": False
        }
    }

class AIConfig:
    """AI模型配置"""
    
    MODELS = {
        "deepseek": {
            "name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "enabled": True,
            "weight": 0.25
        },
        "qwen": {
            "name": "通义千问", 
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "enabled": True,
            "weight": 0.25
        },
        "chatgpt": {
            "name": "ChatGPT",
            "base_url": "https://api.openai.com/v1",
            "enabled": True, 
            "weight": 0.25
        },
        "gemini": {
            "name": "Gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1",
            "enabled": True,
            "weight": 0.25
        }
    }
    
    # AI分析维度
    ANALYSIS_DIMENSIONS = {
        "macro": "宏观经济分析",
        "industry": "行业政策分析", 
        "fundamental": "公司基本面分析",
        "sentiment": "市场情绪分析"
    }