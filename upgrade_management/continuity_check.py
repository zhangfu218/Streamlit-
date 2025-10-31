"""
升级连续性检查脚本
"""
import sys
import os
import datetime  # 添加缺失的导入

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from core import UpgradeStateManager
from validator import UpgradeValidator

def perform_continuity_check():
    """执行连续性检查"""
    print("🔍 执行升级连续性检查...")
    print("=" * 60)
    
    try:
        # 初始化管理器
        manager = UpgradeStateManager()
        validator = UpgradeValidator()
        
        # 显示项目信息
        project_info = manager.state["project_info"]
        print(f"📁 项目: {project_info['name']}")
        print(f"🔗 仓库: {project_info['github_repo']}")
        print(f"🏷️  版本: {project_info['current_version']} → {project_info['target_version']}")
        print()
        
        # 显示升级进度
        progress = manager.get_progress()
        print(f"📊 升级进度: {progress['completed_modules']}/{progress['total_modules']} "
              f"({progress['progress_percent']:.1f}%)")
        print(f"🎯 当前阶段: {progress['current_phase']}")
        print(f"🔧 当前模块: {progress['current_module']}")
        print()
        
        # 显示阶段状态
        print("📋 阶段状态:")
        for phase_id, phase_data in manager.state["upgrade_phases"].items():
            phase_name = phase_data["name"]
            phase_status = phase_data["status"]
            completed_count = sum(1 for m in phase_data["modules"].values() if m["status"] == "completed")
            total_count = len(phase_data["modules"])
            
            status_icon = "✅" if phase_status == "completed" else "🔄" if phase_status == "in_progress" else "⏳"
            print(f"  {status_icon} {phase_name}: {completed_count}/{total_count} 完成")
        
        print()
        
        # 系统健康检查
        health_report = {"all_healthy": False, "missing_modules": []}  # 初始化变量
        print("🏥 系统健康检查:")
        try:
            health_report = validator.validate_system_health()
            if health_report["all_healthy"]:
                print("  ✅ 所有核心依赖正常")
            else:
                print("  ❌ 缺失模块:", ", ".join(health_report["missing_modules"]))
        except Exception as e:
            print(f"  ⚠️ 健康检查失败: {e}")
        
        print()
        
        # 会话历史
        session_history = manager.state.get("session_history", [])[-3:]  # 最近3次会话
        if session_history:
            print("📝 最近会话:")
            for session in session_history:
                session_id = session["session_id"]
                start_time = datetime.datetime.fromisoformat(session["started_at"]).strftime("%m/%d %H:%M")
                status = "✅ 完成" if session.get("completed_at") else "🔄 进行中"
                print(f"  {session_id} ({start_time}): {status}")
        
        print("=" * 60)
        print("🎯 连续性检查完成!")
        
        return {
            "manager": manager,
            "validator": validator,
            "progress": progress,
            "health": health_report
        }
        
    except Exception as e:
        print(f"❌ 连续性检查失败: {e}")
        print("💡 提示: 这可能是首次运行，系统正在初始化...")
        return None

if __name__ == "__main__":
    perform_continuity_check()