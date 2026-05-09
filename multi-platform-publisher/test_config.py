#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from utils.config import Config
import logging
from utils.logger import setup_logging, get_logger

def test_config():
    # 设置日志
    setup_logging(level=logging.INFO, log_file='test.log')
    logger = get_logger('test')
    
    # 加载配置
    config = Config()
    
    # 测试路径配置
    paths = config.get('paths', {})
    logger.info(f"监控目录: {paths.get('watch_dir')}")
    logger.info(f"图片目录: {paths.get('image_dir')}")
    logger.info(f"已发布目录: {paths.get('published_dir')}")
    
    # 测试账户配置
    accounts = config.get('accounts', {})
    for name, account in accounts.items():
        logger.info(f"账户: {name}, 类型: {account.get('type')}")

if __name__ == "__main__":
    import logging
    test_config()
