#!/usr/bin/env python3
"""
修改wechat_publisher.py的md2集成方案
使用本地服务替代无效的md2 API
"""
import os
import sys
import tempfile
import base64
import requests
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_local_md2_image(markdown_content, account_name="default"):
    """
    使用本地服务生成Markdown图片
    替代原有的md2 API调用
    """
    try:
        # 本地服务地址
        api_url = "http://localhost:8081/convert"
        
        payload = {
            "markdown": markdown_content,
            "theme": "default"
        }
        
        logging.info(f"正在调用本地md2服务生成图片...", extra={'account_name': account_name})
        response = requests.post(api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if result.get('code') == 200 and result.get('data', {}).get('image'):
            # 获取base64图片数据
            image_data = result['data']['image']
            
            # 解码base64数据
            if 'base64,' in image_data:
                base64_content = image_data.split('base64,')[1]
                image_bytes = base64.b64decode(base64_content)
                
                # 保存为临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_file.write(image_bytes)
                temp_file.close()
                
                logging.info(f"✓ 本地md2图片生成成功: {temp_file.name}", extra={'account_name': account_name})
                return temp_file.name
            else:
                logging.error(f"图片数据格式错误: {image_data[:100]}...", extra={'account_name': account_name})
                return None
        else:
            logging.error(f"本地md2服务返回错误: {result}", extra={'account_name': account_name})
            return None
            
    except requests.exceptions.ConnectionError:
        logging.error("本地md2服务未启动，请确保服务运行在 http://localhost:8081", extra={'account_name': account_name})
        return None
    except Exception as e:
        logging.error(f"调用本地md2服务失败: {e}", extra={'account_name': account_name})
        return None

def test_local_md2_service():
    """测试本地md2服务"""
    test_markdown = """# 测试标题

这是一段**测试内容**，包含各种格式。

## 子标题

- 列表项1
- 列表项2

```python
def hello_world():
    print("Hello, World!")
```

> 这是一个引用块

普通段落文字，包含*斜体*和**加粗**文本。
"""
    
    logging.basicConfig(level=logging.INFO)
    
    print("正在测试本地md2服务...")
    result = generate_local_md2_image(test_markdown, "测试账号")
    
    if result:
        print(f"✓ 测试成功! 图片已保存到: {result}")
        
        # 验证文件是否存在
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✓ 文件大小: {file_size} 字节")
            return True
        else:
            print("✗ 文件未找到")
            return False
    else:
        print("✗ 测试失败")
        return False

def create_integration_patch():
    """创建集成补丁代码"""
    patch_code = '''
    def _generate_md2_image(self, markdown_content, title):
        """
        使用本地md2服务生成公众号图片
        替代原有的md2 API调用
        """
        try:
            # 本地服务地址
            api_url = "http://localhost:8081/convert"
            
            payload = {
                "markdown": markdown_content,
                "theme": "default"
            }
            
            logging.info(f"正在调用本地md2服务生成图片...", extra={'account_name': self.account_name})
            response = self.image_session.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 200 and result.get('data', {}).get('image'):
                # 获取base64图片数据
                image_data = result['data']['image']
                
                # 解码base64数据
                if 'base64,' in image_data:
                    base64_content = image_data.split('base64,')[1]
                    image_bytes = base64.b64decode(base64_content)
                    
                    # 保存为临时文件
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_bytes)
                    temp_file.close()
                    
                    logging.info(f"✓ 本地md2图片生成成功: {temp_file.name}", extra={'account_name': self.account_name})
                    return temp_file.name
                else:
                    logging.error(f"图片数据格式错误", extra={'account_name': self.account_name})
                    return None
            else:
                logging.error(f"本地md2服务返回错误: {result}", extra={'account_name': self.account_name})
                return None
                
        except requests.exceptions.ConnectionError:
            logging.error("本地md2服务未启动，将使用CSS样式", extra={'account_name': self.account_name})
            return None
        except Exception as e:
            logging.error(f"调用本地md2服务失败: {e}", extra={'account_name': self.account_name})
            return None
'''
    
    return patch_code

if __name__ == "__main__":
    print("本地md2服务集成测试")
    print("=" * 30)
    
    # 测试服务
    if test_local_md2_service():
        print("\n✓ 本地md2服务集成测试通过!")
        print("\n现在可以修改 wechat_publisher.py 中的 _generate_md2_image 方法")
        print("使用上面的 create_integration_patch() 函数中的代码替换原有方法")
    else:
        print("\n✗ 本地md2服务集成测试失败!")
        print("请确保本地服务已启动: python local_markdown_service.py")