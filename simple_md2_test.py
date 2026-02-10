#!/usr/bin/env python3
"""
简单测试md2集成功能
"""
import os
import sys
import tempfile
import requests
import base64

# 测试本地md2服务
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
    
    try:
        # 本地服务地址
        api_url = "http://localhost:8081/convert"
        
        payload = {
            "markdown": test_markdown,
            "theme": "default"
        }
        
        print("正在调用本地md2服务生成图片...")
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
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir='/Users/ax/wechat-publisher')
                temp_file.write(image_bytes)
                temp_file.close()
                
                print(f"✓ 本地md2图片生成成功: {temp_file.name}")
                
                # 验证文件
                if os.path.exists(temp_file.name):
                    file_size = os.path.getsize(temp_file.name)
                    print(f"✓ 文件大小: {file_size} 字节")
                    
                    # 询问是否删除
                    response = input("是否删除临时文件? (y/n): ")
                    if response.lower() == 'y':
                        os.unlink(temp_file.name)
                        print("✓ 临时文件已删除")
                
                return temp_file.name
            else:
                print(f"✗ 图片数据格式错误")
                return None
        else:
            print(f"✗ 本地md2服务返回错误: {result}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 本地md2服务未启动")
        print("请先启动服务: python local_markdown_service.py")
        return None
    except Exception as e:
        print(f"✗ 调用本地md2服务失败: {e}")
        return None

if __name__ == "__main__":
    print("本地md2服务测试工具")
    print("=" * 30)
    
    # 测试服务
    result = test_local_md2_service()
    
    if result:
        print(f"\n✓ 测试成功! 图片已保存到: {result}")
        print("\n现在可以：")
        print("1. 查看生成的图片")
        print("2. 在wechat_publisher.py中使用本地md2服务")
    else:
        print("\n✗ 测试失败!")
        print("请确保：")
        print("1. 本地md2服务已启动 (python local_markdown_service.py)")
        print("2. 服务运行在 http://localhost:8081")