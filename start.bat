@echo off
echo 🚀 启动量子AI交易系统 v6.0...
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 启动主程序
streamlit run app_main.py

pause