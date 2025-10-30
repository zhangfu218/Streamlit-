#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子AI交易系统 - 系统验证脚本
"""

import sys
import importlib

def check_import(module_name):
    """检查模块是否能正常导入"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {module_name}"
    except ImportError as e:
        return False, f"❌ {module_name}: {e}"

def main():
    print("🔍 量子AI交易系统 - 环境验证")
    print("=" * 50)
    
    # 检查核心依赖
    core_modules = [
        'streamlit', 'pandas', 'numpy', 'plotly', 'psutil',
        'sqlite3', 'threading', 'queue', 'json', 'datetime'
    ]
    
    print("📦 检查核心依赖...")
    for module in core_modules:
        success, message = check_import(module)
        print(f"   {message}")
    
    print("\n🔧 检查自定义模块...")
    # 检查自定义模块
    custom_modules = [
        'core.data_manager',
        'core.ai_engine', 
        'core.trading_engine',
        'core.risk_manager',
        'core.portfolio_manager',
        'utils.offline_mode',
        'utils.memory_manager'
    ]
    
    for module in custom_modules:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ⚠️  {module}: {e}")
    
    print("\n🎯 验证完成!")
    print("💡 运行 'start.bat' 启动完整系统")

if __name__ == "__main__":
    main()