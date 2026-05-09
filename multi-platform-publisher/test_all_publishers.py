#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import io
import yaml
from pathlib import Path
from typing import Dict, Any
import importlib

# 设置控制台输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from utils.logger import setup_logging, get_logger
from utils.config import Config
from publishers.base import BasePublisher

# 设置日志
setup_logging()
logger = get_logger('test_publishers')

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = Path('config.yaml')
    if not config_path.exists():
        logger.error("配置文件 config.yaml 不存在")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_publisher(account_name: str, publisher: BasePublisher, test_file: str):
    """测试单个发布器"""
    logger.info(f"测试 {account_name} 发布器...")
    
    if not os.path.exists(test_file):
        logger.warning(f"测试文件 {test_file} 不存在，跳过测试 {account_name}")
        return False
    
    try:
        logger.info(f"正在发布文件: {test_file}")
        result = publisher.process_document(test_file)
        if result:
            logger.info(f"{account_name} 发布成功！")
        else:
            logger.warning(f"{account_name} 发布失败")
        return result
    except Exception as e:
        logger.error(f"{account_name} 发布过程中发生错误: {e}", exc_info=True)
        return False

def main():
    # 加载配置
    config = Config()
    
    # 初始化发布器
    publishers = {}
    for account_name, account_config in config.get_accounts().items():
        try:
            platform = account_config.get('platform')
            if not platform:
                logger.warning(f"账户 {account_name} 未指定平台，跳过")
                continue
                
            # 动态导入发布器模块
            module_name = f"publishers.{platform}_publisher"
            try:
                module = importlib.import_module(module_name)
                publisher_class = getattr(module, f"{platform.capitalize()}Publisher", None)
                if not publisher_class:
                    logger.warning(f"未找到 {platform} 的发布器类，跳过")
                    continue
                    
                # 初始化发布器
                publisher = publisher_class(account_name, account_config, config)
                publishers[account_name] = publisher
                logger.info(f"成功初始化 {account_name} 发布器 ({platform})")
                
            except ImportError as e:
                logger.warning(f"无法导入 {module_name}: {e}")
                continue
                
        except Exception as e:
            logger.error(f"初始化 {account_name} 发布器时出错: {e}", exc_info=True)
    
    if not publishers:
        logger.error("没有可用的发布器")
        return
    
    # 测试每个发布器
    test_files = {
        "AI流习社": "documents/码趣逻辑站/python第四课.md",
        "开源智核": "documents/开源智核/告别Token黑箱，Karpathy封神.md",
        "码趣逻辑站": "documents/码趣逻辑站/python第四课.md",
        "CSDN博客": "documents/码趣逻辑站/python第四课.md",
        "技术头条": "documents/码趣逻辑站/python第四课.md",
        "技术专栏": "documents/码趣逻辑站/python第四课.md"
    }
    
    for account_name, publisher in publishers.items():
        test_file = test_files.get(account_name)
        if not test_file:
            logger.warning(f"未找到 {account_name} 的测试文件，跳过")
            continue
            
        test_publisher(account_name, publisher, test_file)
    
    logger.info("测试完成")

if __name__ == "__main__":
    main()
