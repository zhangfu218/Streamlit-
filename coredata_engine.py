# 在文件开头添加
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import akshare as ak
import yfinance as yf
import ccxt
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
import threading
import time
import json
import pandas as pd
import numpy as np
import akshare as ak
import yfinance as yf
import ccxt
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import json

class QuantumDataEngine:
    """量子数据引擎 - 支持全市场实时数据"""
    
    def __init__(self):
        self.connected = True
        self.last_success = datetime.now()
        self.data_cache = {}
        self.setup_database()
        self.start_health_check()
    
    def setup_database(self):
        """初始化数据库"""
        conn = sqlite3.connect('data/database/trading_system.db')

# 在适当的位置添加这些修复
def _get_ashare_data(self, symbol: str):
    """获取A股数据"""
    try:
        # 移除前导零点
        clean_symbol = symbol.replace('.', '')
        # 其他代码保持不变
        
        # 创建股票数据表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                code TEXT,
                market TEXT,
                timestamp DATETIME,
                open REAL,
                high REAL,
                low REAL, 
                close REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (code, market, timestamp)
            )
        ''')
        
        # 创建技术指标表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                code TEXT,
                market TEXT, 
                timestamp DATETIME,
                ma5 REAL,
                ma20 REAL,
                ma60 REAL,
                rsi REAL,
                macd REAL,
                macd_signal REAL,
                boll_upper REAL,
                boll_lower REAL,
                PRIMARY KEY (code, market, timestamp)
            )
        ''')
        
        # 创建新闻数据表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news_data (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                sentiment REAL,
                related_stocks TEXT,
                publish_time DATETIME,
                source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_health_check(self):
        """启动健康检查线程"""
        def health_monitor():
            while True:
                try:
                    # 测试数据连接
                    test_result = self.test_connections()
                    self.connected = any(test_result.values())
                    
                    if self.connected:
                        self.last_success = datetime.now()
                    
                    time.sleep(60)  # 每分钟检查一次
                    
                except Exception as e:
                    print(f"健康检查异常: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=health_monitor, daemon=True)
        thread.start()
    
    def test_connections(self) -> Dict[str, bool]:
        """测试数据源连接"""
        results = {}
        
        try:
            # 测试A股数据
            df = ak.stock_zh_a_spot_em()
            results['akshare'] = not df.empty
        except:
            results['akshare'] = False
        
        try:
            # 测试美股数据
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            results['yfinance'] = bool(info)
        except:
            results['yfinance'] = False
            
        return results
    
    async def get_real_time_data(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情数据"""
        all_data = []
        
        for symbol in symbols:
            try:
                if self.connected:
                    data = await self._fetch_online_data(symbol)
                else:
                    data = self._get_cached_data(symbol)
                
                if data is not None:
                    all_data.append(data)
                    
            except Exception as e:
                print(f"获取{symbol}数据失败: {e}")
                # 使用缓存数据
                cached = self._get_cached_data(symbol)
                if cached is not None:
                    all_data.append(cached)
        
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    
    async def _fetch_online_data(self, symbol: str) -> Optional[Dict]:
        """在线获取数据"""
        try:
            # 根据符号类型选择数据源
            if symbol.endswith('.SS') or symbol.endswith('.SZ'):
                # A股数据
                return await self._get_ashare_data(symbol)
            elif symbol.endswith('.HK'):
                # 港股数据
                return await self._get_hk_data(symbol)
            elif '.' not in symbol:
                # 美股数据
                return await self._get_us_data(symbol)
            else:
                return None
                
        except Exception as e:
            print(f"在线获取{symbol}数据异常: {e}")
            return None
    
    async def _get_ashare_data(self, symbol: str) -> Dict:
        """获取A股数据"""
        # 使用akshare获取A股实时数据
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == symbol.replace('.', '')].iloc[0]
        
        return {
            'symbol': symbol,
            'name': stock_data['名称'],
            'price': stock_data['最新价'],
            'change': stock_data['涨跌幅'],
            'volume': stock_data['成交量'],
            'amount': stock_data['成交额'],
            'high': stock_data['最高'],
            'low': stock_data['最低'],
            'open': stock_data['今开'],
            'pre_close': stock_data['昨收']
        }
    
    async def _get_us_data(self, symbol: str) -> Dict:
        """获取美股数据"""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': hist['Close'].iloc[-1],
                'change': (hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1] * 100,
                'volume': hist['Volume'].iloc[-1],
                'amount': hist['Close'].iloc[-1] * hist['Volume'].iloc[-1],
                'high': hist['High'].iloc[-1],
                'low': hist['Low'].iloc[-1],
                'open': hist['Open'].iloc[-1],
                'pre_close': hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
            }
        return None
    
    def _get_cached_data(self, symbol: str) -> Optional[Dict]:
        """获取缓存数据"""
        # 从数据库获取最新缓存数据
        conn = sqlite3.connect('data/database/trading_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM stock_data 
            WHERE code = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'symbol': row[0],
                'price': row[5],  # close price
                'timestamp': row[2]
            }
        return None
    
    def get_technical_indicators(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """获取技术指标"""
        try:
            if symbol.endswith('.SS') or symbol.endswith('.SZ'):
                # A股技术指标
                stock_code = symbol.replace('.', '')
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="hfq")
            else:
                # 美股技术指标
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
            
            # 计算技术指标
            df = self._calculate_technical_indicators(df)
            return df
            
        except Exception as e:
            print(f"计算技术指标失败 {symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        if df.empty:
            return df
        
        # 移动平均线
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # 布林带
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        return df