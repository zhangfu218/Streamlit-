"""
升级连续性系统核心模块
"""
import json
import os
import pickle
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import git
import yaml

class UpgradeStateManager:
    """升级状态管理器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.state_file = self.repo_path / "upgrade_management" / "upgrade_state.json"
        self.checkpoints_dir = self.repo_path / "upgrade_management" / "checkpoints"
        self.backups_dir = self.repo_path / "upgrade_management" / "backups"
        
        # 确保目录存在
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或初始化状态
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """加载升级状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._initialize_state()
    
    def _initialize_state(self) -> Dict[str, Any]:
        """初始化升级状态"""
        initial_state = {
            "project_info": {
                "name": "Streamlit智能投资系统",
                "github_repo": "https://github.com/zhangfu218/Streamlit-",
                "current_version": "1.0",
                "target_version": "2.0"
            },
            "upgrade_phases": {
                "phase_1": {
                    "name": "基础质变",
                    "status": "pending",  # pending, in_progress, completed
                    "modules": {
                        "multimodal_ai": {"status": "pending", "started_at": None, "completed_at": None},
                        "adaptive_learning": {"status": "pending", "started_at": None, "completed_at": None},
                        "auto_reporting": {"status": "pending", "started_at": None, "completed_at": None},
                        "workflow_orchestration": {"status": "pending", "started_at": None, "completed_at": None}
                    }
                },
                "phase_2": {
                    "name": "生态构建", 
                    "status": "pending",
                    "modules": {
                        "open_api": {"status": "pending", "started_at": None, "completed_at": None},
                        "multi_agent": {"status": "pending", "started_at": None, "completed_at": None},
                        "causal_reasoning": {"status": "pending", "started_at": None, "completed_at": None},
                        "user_profiling": {"status": "pending", "started_at": None, "completed_at": None}
                    }
                }
            },
            "current_phase": "phase_1",
            "current_module": None,
            "session_history": [],
            "last_updated": datetime.datetime.now().isoformat()
        }
        self._save_state(initial_state)
        return initial_state
    
    def _save_state(self, state: Dict[str, Any]):
        """保存升级状态"""
        state["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def start_session(self, session_type: str = "upgrade") -> str:
        """开始新会话"""
        session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_info = {
            "session_id": session_id,
            "type": session_type,
            "started_at": datetime.datetime.now().isoformat(),
            "completed_at": None,
            "goals": [],
            "achievements": [],
            "challenges": [],
            "next_steps": []
        }
        
        self.state["session_history"].append(session_info)
        self.state["current_session"] = session_id
        self._save_state(self.state)
        
        return session_id
    
    def end_session(self, achievements: List[str] = None, next_steps: List[str] = None):
        """结束当前会话"""
        if achievements is None:
            achievements = []
        if next_steps is None:
            next_steps = []
            
        current_session_id = self.state.get("current_session")
        if current_session_id:
            for session in self.state["session_history"]:
                if session["session_id"] == current_session_id:
                    session["completed_at"] = datetime.datetime.now().isoformat()
                    session["achievements"] = achievements
                    session["next_steps"] = next_steps
                    break
        
        self.state["current_session"] = None
        self._save_state(self.state)
    
    def start_module(self, phase: str, module: str):
        """开始处理模块"""
        if phase in self.state["upgrade_phases"]:
            if module in self.state["upgrade_phases"][phase]["modules"]:
                self.state["upgrade_phases"][phase]["modules"][module]["status"] = "in_progress"
                self.state["upgrade_phases"][phase]["modules"][module]["started_at"] = datetime.datetime.now().isoformat()
                self.state["upgrade_phases"][phase]["status"] = "in_progress"
                self.state["current_phase"] = phase
                self.state["current_module"] = module
                self._save_state(self.state)
    
    def complete_module(self, phase: str, module: str):
        """完成模块"""
        if phase in self.state["upgrade_phases"]:
            if module in self.state["upgrade_phases"][phase]["modules"]:
                self.state["upgrade_phases"][phase]["modules"][module]["status"] = "completed"
                self.state["upgrade_phases"][phase]["modules"][module]["completed_at"] = datetime.datetime.now().isoformat()
                self._save_state(self.state)
                
                # 检查阶段是否完成
                self._check_phase_completion(phase)
    
    def _check_phase_completion(self, phase: str):
        """检查阶段是否完成"""
        phase_data = self.state["upgrade_phases"][phase]
        all_completed = all(
            module["status"] == "completed" 
            for module in phase_data["modules"].values()
        )
        
        if all_completed:
            phase_data["status"] = "completed"
            self._save_state(self.state)
    
    def get_progress(self) -> Dict[str, Any]:
        """获取升级进度"""
        total_modules = 0
        completed_modules = 0
        
        for phase in self.state["upgrade_phases"].values():
            for module in phase["modules"].values():
                total_modules += 1
                if module["status"] == "completed":
                    completed_modules += 1
        
        progress_percent = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        return {
            "total_modules": total_modules,
            "completed_modules": completed_modules,
            "progress_percent": progress_percent,
            "current_phase": self.state["current_phase"],
            "current_module": self.state["current_module"]
        }
    
    def create_checkpoint(self, description: str):
        """创建检查点"""
        checkpoint_id = f"checkpoint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "description": description,
            "created_at": datetime.datetime.now().isoformat(),
            "state": self.state.copy(),
            "git_info": self._get_git_info()
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        return checkpoint_id
    
    def _get_git_info(self) -> Dict[str, Any]:
        """获取Git信息"""
        try:
            repo = git.Repo(self.repo_path)
            return {
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha,
                "message": repo.head.commit.message.strip()
            }
        except:
            return {"branch": "unknown", "commit": "unknown", "message": "unknown"}