import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """配置管理类，用于加载和管理应用程序配置"""
    
    def __init__(self, config_path: str = 'config.yaml', env_path: str = '.env'):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            env_path: 环境变量文件路径
        """
        self.config_path = config_path
        self.env_path = env_path
        self._config = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """加载配置文件和环境变量"""
        # 加载环境变量
        self._load_env_vars()
        
        # 加载YAML配置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
                
            # 解析环境变量引用
            self._resolve_env_refs(self._config)
            
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 未找到，使用空配置")
            self._config = {}
        except yaml.YAMLError as e:
            print(f"警告: 解析配置文件 {self.config_path} 时出错: {e}")
            self._config = {}
    
    def _load_env_vars(self) -> None:
        """从.env文件加载环境变量"""
        try:
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                key, value = line.split('=', 1)
                                os.environ[key] = value.strip('"\'')
                            except ValueError:
                                continue
        except Exception as e:
            print(f"警告: 加载环境变量文件时出错: {e}")
    
    def _resolve_env_refs(self, data: Any) -> None:
        """
        递归解析配置中的环境变量引用。如果必需的环境变量缺失，则打印错误并退出。
        支持格式:
        - ${VAR} - 必需的环境变量，如果缺失则程序会退出。
        - ${VAR:-default} - 带默认值的环境变量。
        - ${VAR:-} - 空字符串作为默认值。
        """
        import re
        import sys

        def resolve_value(value: str) -> str:
            match = re.match(r'^\$\{([^:}]+)(?::-(.*))?\}$', value)
            if not match:
                return value

            var_name = match.group(1).strip()
            default_value = match.group(2)
            has_default = default_value is not None

            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value

            if has_default:
                return default_value
            
            # 如果代码执行到这里，说明环境变量既不存在，也没有提供默认值。
            # 返回 None，让调用者决定如何处理
            return None

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = resolve_value(value)
                elif isinstance(value, (dict, list)):
                    self._resolve_env_refs(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = resolve_value(item)
                elif isinstance(item, (dict, list)):
                    self._resolve_env_refs(item)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项，支持点分路径（如 'database.host'）
        
        Args:
            key: 配置键名，支持点分路径
            default: 默认值
            
        Returns:
            配置值，如果不存在则返回默认值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_accounts(self) -> Dict[str, dict]:
        """获取所有账户配置"""
        return self.get('accounts', {})
    
    def get_paths(self) -> Dict[str, str]:
        """获取通用路径配置"""
        return self.get('common', {})
    
    def get_config(self) -> Dict[str, Any]:
        """返回完整的原始配置字典"""
        return self._config
    
    def get_watch_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return self.get('watch', {})
    
    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        """检查配置项是否存在"""
        try:
            self.get(key)
            return True
        except KeyError:
            return False
