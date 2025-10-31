"""
升级会话模板
"""
import datetime

def generate_session_template(manager, previous_session=None):
    """生成会话模板"""
    
    template = f"""
## 🔄 升级连续性确认 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

### 📍 项目基准信息
- **项目**: {manager.state['project_info']['name']}
- **仓库**: {manager.state['project_info']['github_repo']}  
- **版本**: {manager.state['project_info']['current_version']} → {manager.state['project_info']['target_version']}

### 📊 当前升级进度
"""
    
    progress = manager.get_progress()
    template += f"- **总体进度**: {progress['completed_modules']}/{progress['total_modules']} ({progress['progress_percent']:.1f}%)\n"
    template += f"- **当前阶段**: {progress['current_phase']}\n"
    template += f"- **当前模块**: {progress['current_module'] or '无'}\n\n"
    
    if previous_session:
        template += f"### 📝 前次会话回顾 ({previous_session['session_id']})\n"
        if previous_session['achievements']:
            template += "**完成的任务**:\n"
            for achievement in previous_session['achievements']:
                template += f"- ✅ {achievement}\n"
        if previous_session['challenges']:
            template += "**遇到的挑战**:\n"  
            for challenge in previous_session['challenges']:
                template += f"- ⚠️ {challenge}\n"
        if previous_session['next_steps']:
            template += "**原定下一步**:\n"
            for step in previous_session['next_steps']:
                template += f"- ➡️ {step}\n"
        template += "\n"
    
    template += """### 🎯 本次会话目标
请明确本次会话的具体目标：

1. [具体目标1]
2. [具体目标2] 
3. [具体目标3]

### 🔍 依赖验证清单
- [ ] 确认前置任务已完成
- [ ] 验证相关模块运行正常  
- [ ] 检查API密钥和配置
- [ ] 确认数据源可用性

### 📋 行动计划
[具体实施步骤...]

---
*此模板由升级连续性系统自动生成*
"""
    
    return template

def start_new_upgrade_session(manager, session_goals):
    """开始新的升级会话"""
    session_id = manager.start_session("upgrade")
    
    # 获取最近完成的会话
    previous_session = None
    for session in reversed(manager.state["session_history"]):
        if session["session_id"] != session_id and session["completed_at"]:
            previous_session = session
            break
    
    template = generate_session_template(manager, previous_session)
    
    print("🎉 新升级会话已开始!")
    print(f"📝 会话ID: {session_id}")
    print("\n" + "="*60)
    print(template)
    print("="*60)
    
    return session_id