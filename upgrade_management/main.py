"""
升级连续性系统主控制器
"""
import sys
import os
from core import UpgradeStateManager
from validator import UpgradeValidator  
from continuity_check import perform_continuity_check
from session_template import start_new_upgrade_session

def main():
    """主控制函数"""
    
    print("🚀 Streamlit智能投资系统 - 升级连续性系统")
    print("=" * 60)
    
    # 执行连续性检查
    check_results = perform_continuity_check()
    manager = check_results["manager"]
    
    print()
    print("请选择操作:")
    print("1. 开始新升级会话")
    print("2. 验证特定模块")
    print("3. 查看详细进度")
    print("4. 创建检查点")
    print("5. 退出")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == "1":
        goals = input("请输入本次会话目标 (用逗号分隔): ").split(",")
        session_id = start_new_upgrade_session(manager, [goal.strip() for goal in goals])
        
        print(f"\n💡 提示: 在开始编码前，请运行:")
        print(f"python -m upgrade_management.continuity_check")
        print(f"当前会话ID: {session_id}")
    
    elif choice == "2":
        module_name = input("请输入要验证的模块名称: ").strip()
        validator = UpgradeValidator()
        result = validator.validate_module(module_name)
        
        print(f"\n验证结果 - {module_name}:")
        if result["valid"]:
            print("✅ 验证通过!")
        else:
            print("❌ 验证失败:")
            for validation in result["results"]:
                if not validation["valid"]:
                    print(f"  - {validation['error']}")
    
    elif choice == "3":
        progress = manager.get_progress()
        print(f"\n📊 详细进度报告:")
        print(f"总体进度: {progress['progress_percent']:.1f}%")
        
        for phase_id, phase_data in manager.state["upgrade_phases"].items():
            print(f"\n{phase_data['name']} ({phase_data['status']}):")
            for module_name, module_data in phase_data["modules"].items():
                status_icon = "✅" if module_data["status"] == "completed" else "🔄" if module_data["status"] == "in_progress" else "⏳"
                print(f"  {status_icon} {module_name}")
    
    elif choice == "4":
        description = input("请输入检查点描述: ").strip()
        checkpoint_id = manager.create_checkpoint(description)
        print(f"✅ 检查点已创建: {checkpoint_id}")
    
    elif choice == "5":
        print("👋 再见!")
        sys.exit(0)
    
    else:
        print("❌ 无效选择!")

if __name__ == "__main__":
    main()