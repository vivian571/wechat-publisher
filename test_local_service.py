#!/usr/bin/env python3
"""
测试本地Markdown转换服务
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get("http://localhost:8081/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✓ 健康检查通过: {data}")
            return True
        else:
            logging.error(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"✗ 健康检查异常: {e}")
        return False

def test_convert_api():
    """测试转换接口"""
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
    
    payload = {
        "markdown": test_markdown,
        "theme": "default"
    }
    
    try:
        response = requests.post(
            "http://localhost:8081/convert",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                logging.info("✓ 转换接口测试成功")
                logging.info(f"✓ 返回数据长度: {len(str(data))}")
                
                # 保存base64图片
                image_data = data.get("data", {}).get("image", "")
                if image_data:
                    # 提取base64部分
                    if "base64," in image_data:
                        base64_content = image_data.split("base64,")[1]
                        
                        # 解码并保存图片
                        import base64
                        with open("/Users/ax/wechat-publisher/local_service_test.png", "wb") as f:
                            f.write(base64.b64decode(base64_content))
                        
                        logging.info("✓ 图片已保存到: /Users/ax/wechat-publisher/local_service_test.png")
                
                return True
            else:
                logging.error(f"✗ 转换失败: {data.get('msg')}")
                return False
        else:
            logging.error(f"✗ 接口返回错误: {response.status_code}")
            logging.error(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"✗ 转换接口异常: {e}")
        return False

def test_real_article():
    """测试真实文章内容"""
    real_markdown = """# Cursor 之后，它可能是最懂开发者的"赛博工友"：深度评测 Shannon AI Hacker

> 当 AI 编程助手开始理解你的代码风格、项目上下文，甚至能预测你的下一步操作，编程体验会发生怎样的质变？

## 引言

在过去的一年里，AI 编程助手从简单的代码补全工具，进化成了能理解整个项目结构的智能伙伴。但大多数工具仍然停留在"被动响应"的层面——你需要明确告诉它们做什么。

**Shannon AI Hacker** 的出现，似乎要打破这个局面。它号称是"最懂开发者的 AI 编程助手"，不仅能理解你的代码，还能主动发现问题、提供解决方案，甚至预测你的开发需求。

## 核心特性

### 1. 智能代码理解
- **上下文感知**：理解整个项目的代码结构和业务逻辑
- **风格学习**：学习并适应你的编码风格
- **主动建议**：在编码过程中主动提供优化建议

### 2. 预测性编程
```python
def process_user_data(user_data):
    # Shannon AI 预测：你可能需要数据验证
    if not user_data.get('email'):
        raise ValueError("Email is required")
    
    # 预测：接下来可能需要数据清洗
    cleaned_data = user_data.strip()
    return cleaned_data
```

### 3. 智能调试助手
当代码出现问题时，Shannon AI 不仅能指出错误，还能：

> "根据你的代码模式，这个错误通常是由于异步处理不当导致的。建议检查第 42 行的 await 调用。"

## 实际体验

经过两周的深度使用，我发现 Shannon AI Hacker 确实有一些独特的优势：

1. **学习能力强**：能快速适应我的编码习惯
2. **预测准确**：经常能在我需要之前就提供相关建议
3. **上下文理解**：能准确理解项目的业务逻辑
4. **响应迅速**：几乎没有明显的延迟感

## 总结

Shannon AI Hacker 代表了 AI 编程助手的新方向——从被动工具向主动伙伴的转变。虽然它还不能完全替代开发者的思考，但确实能显著提升开发效率。

对于追求高效率的开发者来说，这绝对是一个值得尝试的工具。
"""
    
    payload = {
        "markdown": real_markdown,
        "theme": "default"
    }
    
    try:
        response = requests.post(
            "http://localhost:8081/convert",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # 更长的超时时间
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                logging.info("✓ 真实文章转换成功")
                
                # 保存图片
                image_data = data.get("data", {}).get("image", "")
                if image_data and "base64," in image_data:
                    base64_content = image_data.split("base64,")[1]
                    
                    import base64
                    with open("/Users/ax/wechat-publisher/real_article_test.png", "wb") as f:
                        f.write(base64.b64decode(base64_content))
                    
                    logging.info("✓ 真实文章图片已保存到: /Users/ax/wechat-publisher/real_article_test.png")
                
                return True
            else:
                logging.error(f"✗ 真实文章转换失败: {data.get('msg')}")
                return False
        else:
            logging.error(f"✗ 真实文章接口错误: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"✗ 真实文章测试异常: {e}")
        return False

if __name__ == "__main__":
    logging.info("开始测试本地Markdown转换服务...")
    
    # 1. 测试健康检查
    if not test_health_check():
        logging.error("服务未启动或不可用")
        exit(1)
    
    # 2. 测试简单转换
    if test_convert_api():
        logging.info("✓ 简单转换测试通过")
    else:
        logging.error("✗ 简单转换测试失败")
    
    # 3. 测试真实文章
    if test_real_article():
        logging.info("✓ 真实文章测试通过")
    else:
        logging.error("✗ 真实文章测试失败")
    
    logging.info("测试完成!")