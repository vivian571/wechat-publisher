#!/usr/bin/env python3
"""
测试完整的md2集成方案
验证本地服务与wechat_publisher的集成
"""
import os
import sys
import tempfile
import logging
from pathlib import Path

# 添加wechat_publisher路径
sys.path.append('/Users/ax/wechat-publisher/wechat/wechat_publisher')

try:
    from wechat_publisher import WeChatPublisher
except ImportError as e:
    print(f"导入WeChatPublisher失败: {e}")
    print("请确保在正确的环境中运行")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_md2_integration():
    """测试md2集成功能"""
    
    # 测试文章内容
    test_markdown = """# Cursor 之后，它可能是最懂开发者的"赛博工友"：深度评测 Shannon AI Hacker

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
    
    print("开始测试md2集成功能...")
    print("=" * 50)
    
    # 创建临时发布者实例
    try:
        publisher = WeChatPublisher("测试账号")
        print("✓ WeChatPublisher实例创建成功")
    except Exception as e:
        print(f"✗ WeChatPublisher实例创建失败: {e}")
        return False
    
    # 测试md2图片生成功能
    print("\n测试md2图片生成功能...")
    try:
        # 直接测试_generate_md2_image方法
        image_path = publisher._generate_md2_image(test_markdown, "测试文章标题")
        
        if image_path and os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✓ md2图片生成成功: {image_path}")
            print(f"✓ 图片大小: {file_size} 字节")
            
            # 清理临时文件
            try:
                os.unlink(image_path)
                print("✓ 临时文件已清理")
            except:
                pass
                
        else:
            print("✗ md2图片生成失败或文件不存在")
            return False
            
    except Exception as e:
        print(f"✗ md2图片生成异常: {e}")
        return False
    
    # 测试完整的HTML包装功能
    print("\n测试HTML包装功能...")
    try:
        # 将Markdown转换为HTML
        import markdown
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables'])
        html_content = md.convert(test_markdown)
        
        # 测试_wrap_html_with_style方法
        styled_html = publisher._wrap_html_with_style(html_content, "测试文章标题")
        
        if styled_html and len(styled_html) > 0:
            print(f"✓ HTML包装成功，内容长度: {len(styled_html)}")
            
            # 检查是否包含base64图片
            if "data:image/png;base64," in styled_html:
                print("✓ 检测到base64图片数据")
            else:
                print("⚠ 未检测到base64图片数据，可能使用了CSS样式")
                
            # 保存结果供检查
            output_path = "/Users/ax/wechat-publisher/test_md2_integration_result.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            print(f"✓ 结果已保存到: {output_path}")
            
        else:
            print("✗ HTML包装失败")
            return False
            
    except Exception as e:
        print(f"✗ HTML包装异常: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ md2集成测试全部通过!")
    print("\n现在可以使用md2格式发布文章了！")
    return True

def check_local_service():
    """检查本地服务状态"""
    import requests
    
    try:
        response = requests.get("http://localhost:8081/health", timeout=5)
        if response.status_code == 200:
            print("✓ 本地md2服务运行正常")
            return True
        else:
            print(f"✗ 本地md2服务异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 本地md2服务未启动")
        print("请先启动服务: python local_markdown_service.py")
        return False
    except Exception as e:
        print(f"✗ 检查服务状态失败: {e}")
        return False

if __name__ == "__main__":
    print("md2集成测试工具")
    print("=" * 30)
    
    # 检查本地服务
    if not check_local_service():
        exit(1)
    
    # 运行集成测试
    if test_md2_integration():
        print("\n🎉 恭喜！md2功能已完全可用！")
        print("\n现在所有三个账号都可以使用md2格式发布文章了：")
        print("- AI流习社")
        print("- 开源智核") 
        print("- 平凡日子记")
    else:
        print("\n❌ 测试失败，请检查配置和日志")