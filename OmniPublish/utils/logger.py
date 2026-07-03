"""
日志系统配置
"""

import sys
from loguru import logger
from pathlib import Path


def setup_logger(log_level: str = "INFO"):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    """
    # 移除默认处理器
    logger.remove()
    
    # 🔧 关键修复: 在 Windows 上强制设置控制台编码为 UTF-8
    if sys.platform == 'win32':
        import os
        import io
        
        # 设置控制台代码页为 UTF-8 (65001)
        os.system('chcp 65001 >nul 2>&1')
        
        # 重新包装 stdout 和 stderr 为 UTF-8 编码
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8', 
            errors='replace',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8', 
            errors='replace',
            line_buffering=True
        )
    
    # 控制台输出 (Windows 下禁用颜色,避免编码问题)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=False  # Windows 下禁用颜色
    )
    
    # 文件输出 (按日期分割)
    log_dir = Path(".omnipublish/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "publish_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        encoding="utf-8"
    )
    
    # 错误日志单独记录
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8"
    )
    
    logger.debug(f"日志系统已初始化,级别: {log_level}")


if __name__ == "__main__":
    setup_logger("DEBUG")
    
    logger.debug("这是 DEBUG 消息")
    logger.info("这是 INFO 消息")
    logger.warning("这是 WARNING 消息")
    logger.error("这是 ERROR 消息")
    
    print("✅ Logger 测试通过")
