#!/usr/bin/env python3
"""
测试md2 API的脚本
"""
import os
import requests
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_env_file():
    """加载.env文件"""
    env_path = Path(__file__).parent / 'wechat' / 'wechat_publisher' / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
def test_md2_api():
    """测试md2 API"""
    # 加载环境变量
    load_env_file()
    
    md2_api_key = os.getenv('MD2_API_KEY')
    if not md2_api_key:
        logging.error("未配置MD2_API_KEY")
        return False
        
    try:
        # 测试内容
        test_markdown = """# 测试标题

这是一段测试内容。

- 列表项1
- 列表项2

**加粗文本**和*斜体文本*。"""
        
        api_url = "https://www.md2wechat.cn/api/convert"
        headers = {
            'X-API-Key': md2_api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            "markdown": test_markdown,
            "theme": "default"
        }
        
        logging.info(f"正在测试md2 API...")
        logging.info(f"API URL: {api_url}")
        logging.info(f"API Key: {md2_api_key[:10]}...")
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        logging.info(f"响应状态码: {response.status_code}")
        logging.info(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success') and result.get('data', {}).get('imageUrl'):
                image_url = result['data']['imageUrl']
                logging.info(f"✓ md2 API测试成功! 图片URL: {image_url}")
                return True
            else:
                logging.error(f"md2 API返回错误: {result}")
                return False
        else:
            logging.error(f"md2 API请求失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"测试md2 API失败: {e}")
        return False

if __name__ == "__main__":
    success = test_md2_api()
    if success:
        logging.info("✓ md2 API测试通过，可以开始使用md2格式发布文章!")
    else:
        logging.error("✗ md2 API测试失败，需要检查API密钥或配置")