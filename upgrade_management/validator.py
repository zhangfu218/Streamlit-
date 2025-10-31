"""
升级验证器
"""
import importlib
import sys
from typing import Dict, Any, List
from pathlib import Path

class UpgradeValidator:
    """升级任务验证器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """加载验证规则"""
        return {
            "multimodal_ai": [
                {"type": "module_import", "module": "vision_ai"},
                {"type": "module_import", "module": "audio_analysis"},
                {"type": "function_exists", "module": "vision_ai", "function": "analyze_chart_pattern"}
            ],
            "adaptive_learning": [
                {"type": "module_import", "module": "reinforcement_learning"},
                {"type": "class_exists", "module": "reinforcement_learning", "class": "TradingAgent"},
                {"type": "file_exists", "path": "models/rl_models"}
            ],
            "auto_reporting": [
                {"type": "module_import", "module": "report_generator"},
                {"type": "function_exists", "module": "report_generator", "function": "generate_investment_report"}
            ],
            "workflow_orchestration": [
                {"type": "module_import", "module": "workflow_engine"},
                {"type": "class_exists", "module": "workflow_engine", "class": "TradingWorkflow"}
            ]
        }
    
    def validate_module(self, module_name: str) -> Dict[str, Any]:
        """验证特定模块"""
        if module_name not in self.validation_rules:
            return {"valid": False, "errors": [f"未知模块: {module_name}"]}
        
        rules = self.validation_rules[module_name]
        results = []
        all_valid = True
        
        for rule in rules:
            if rule["type"] == "module_import":
                result = self._validate_module_import(rule["module"])
            elif rule["type"] == "function_exists":
                result = self._validate_function_exists(rule["module"], rule["function"])
            elif rule["type"] == "class_exists":
                result = self._validate_class_exists(rule["module"], rule["class"])
            elif rule["type"] == "file_exists":
                result = self._validate_file_exists(rule["path"])
            else:
                result = {"valid": False, "error": f"未知验证类型: {rule['type']}"}
            
            results.append(result)
            if not result["valid"]:
                all_valid = False
        
        return {
            "module": module_name,
            "valid": all_valid,
            "results": results,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _validate_module_import(self, module_name: str) -> Dict[str, Any]:
        """验证模块导入"""
        try:
            importlib.import_module(module_name)
            return {"valid": True, "message": f"模块 {module_name} 导入成功"}
        except ImportError as e:
            return {"valid": False, "error": f"模块 {module_name} 导入失败: {str(e)}"}
    
    def _validate_function_exists(self, module_name: str, function_name: str) -> Dict[str, Any]:
        """验证函数存在"""
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                return {"valid": True, "message": f"函数 {function_name} 存在于模块 {module_name}"}
            else:
                return {"valid": False, "error": f"函数 {function_name} 不存在于模块 {module_name}"}
        except ImportError:
            return {"valid": False, "error": f"无法导入模块 {module_name}"}
    
    def _validate_class_exists(self, module_name: str, class_name: str) -> Dict[str, Any]:
        """验证类存在"""
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                if isinstance(cls, type):
                    return {"valid": True, "message": f"类 {class_name} 存在于模块 {module_name}"}
            return {"valid": False, "error": f"类 {class_name} 不存在于模块 {module_name}"}
        except ImportError:
            return {"valid": False, "error": f"无法导入模块 {module_name}"}
    
    def _validate_file_exists(self, file_path: str) -> Dict[str, Any]:
        """验证文件存在"""
        full_path = self.repo_path / file_path
        if full_path.exists():
            return {"valid": True, "message": f"文件 {file_path} 存在"}
        else:
            return {"valid": False, "error": f"文件 {file_path} 不存在"}
    
    def validate_system_health(self) -> Dict[str, Any]:
        """验证系统健康状态"""
        core_modules = [
            "streamlit", "pandas", "numpy", "requests",
            "yfinance", "ta", "sklearn", "torch"
        ]
        
        results = []
        missing_modules = []
        
        for module in core_modules:
            try:
                importlib.import_module(module)
                results.append({"module": module, "status": "OK"})
            except ImportError:
                results.append({"module": module, "status": "MISSING"})
                missing_modules.append(module)
        
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "core_modules": results,
            "missing_modules": missing_modules,
            "all_healthy": len(missing_modules) == 0
        }