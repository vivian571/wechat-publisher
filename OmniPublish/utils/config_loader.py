"""
配置加载器
负责加载和解析 config.yaml
"""

import yaml
import os
from pathlib import Path
from loguru import logger


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        self.config = self._load_config()
        logger.debug(f"加载配置文件: {config_path}")
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 替换环境变量
            return self._replace_env_vars(config)
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _replace_env_vars(self, obj):
        """递归替换环境变量"""
        if isinstance(obj, dict):
            return {k: self._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            value = os.getenv(env_var, '')
            if not value:
                logger.warning(f"环境变量未设置: {env_var}")
            return value
        else:
            return obj
    
    def get(self, key_path: str, default=None):
        """
        获取配置值 (支持点号路径)
        
        Args:
            key_path: 配置路径,如 "platforms.devto.api_key"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_platform_config(self, platform: str) -> dict:
        """
        获取平台配置
        
        Args:
            platform: 平台名称 (如 devto, hashnode)
        
        Returns:
            dict: 平台配置
        """
        return self.get(f'platforms.{platform}', {})
    
    def is_platform_enabled(self, platform: str) -> bool:
        """
        检查平台是否启用
        
        Args:
            platform: 平台名称
        
        Returns:
            bool: 是否启用
        """
        return self.get(f'platforms.{platform}.enabled', False)


if __name__ == "__main__":
    # 测试代码
    import sys
    from loguru import logger
    from dotenv import load_dotenv
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    # 加载环境变量
    load_dotenv()
    
    # 测试配置加载
    try:
        config = ConfigLoader("config.yaml")
        
        print(f"Dev.to 启用: {config.is_platform_enabled('devto')}")
        print(f"图床提供商: {config.get('image_storage.provider')}")
        print(f"日志级别: {config.get('global.log_level')}")
        
        print("✅ ConfigLoader 测试通过")
    except FileNotFoundError:
        print("⚠️ 需要先创建 config.yaml 文件")
