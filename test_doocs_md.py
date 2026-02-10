#!/usr/bin/env python3
"""
测试doocs/md容器进行Markdown转换的脚本
"""
import requests
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_doocs_md_conversion():
    """测试doocs/md容器转换"""
    try:
        # 测试内容 - 使用AI流习社的文章内容
        test_markdown = """# Cursor 之后，它可能是最懂开发者的"赛博工友"：深度评测 Shannon AI Hacker

在 AI 编程助手赛道竞争白热化的今天，Cursor 凭借其出色的代码理解和生成能力，已经成为众多开发者的首选工具。然而，技术迭代永不止步，新的挑战者正在崛起。今天，我们要深度评测的主角是 Shannon AI Hacker——一款号称"更懂开发者"的 AI 编程助手。

## 初识 Shannon AI Hacker：不只是另一个 AI 助手

与市面上大多数 AI 编程助手不同，Shannon AI Hacker 从设计之初就定位为一个"赛博工友"——它不仅仅是帮你写代码的工具，更是能够理解你编程思维、工作习惯的智能伙伴。

### 核心特性一览

**深度代码理解**: Shannon AI Hacker 采用了最新的多模态架构，不仅能理解代码本身，还能理解代码背后的业务逻辑和架构设计。

**上下文感知**: 它能够记住你之前的编程决策，在后续的开发中保持一致性。

**智能调试**: 不只是发现错误，更能理解错误的根本原因并提供修复建议。

## 实际体验：从安装到深度使用

### 安装与配置

Shannon AI Hacker 的安装过程非常简洁，支持主流的 IDE 插件市场。我们以 VS Code 为例：

```bash
# 通过 VS Code 插件市场搜索 "Shannon AI Hacker"
# 或者直接下载安装包
```

配置过程同样简单，只需要设置基本的编程语言偏好和项目类型即可开始使用。

### 代码生成能力测试

我们设计了一系列测试场景来评估 Shannon AI Hacker 的代码生成能力：

**场景一：复杂业务逻辑**

当我们要求它生成一个用户认证系统时，Shannon AI Hacker 不仅生成了基本的登录注册功能，还主动考虑了安全性、性能优化、错误处理等细节。

**场景二：代码重构**

在重构一个遗留项目时，它能够理解原有代码的业务逻辑，并在保持功能不变的前提下提供更优雅的实现方案。

**场景三：跨语言支持**

Shannon AI Hacker 在 Python、JavaScript、Go、Rust 等多种语言上都表现出色，能够根据语言特性生成符合最佳实践的代码。

## 深度分析：技术架构与创新点

### 多模态理解引擎

Shannon AI Hacker 的核心是一个多模态理解引擎，它能够同时处理：

- **代码语义**: 理解代码的功能和逻辑
- **项目结构**: 理解代码在整体架构中的位置
- **开发历史**: 分析代码的演进过程
- **团队协作**: 考虑多人协作的编程规范

### 个性化学习机制

最让我们印象深刻的是它的个性化学习能力。Shannon AI Hacker 会：

- 学习你的编程风格和偏好
- 记住你常用的设计模式和架构决策
- 根据项目特点调整建议策略
- 在团队环境中平衡个人偏好和团队规范

## 性能表现：速度与准确性的完美平衡

在实际测试中，Shannon AI Hacker 展现出了令人满意的性能表现：

**响应速度**: 平均响应时间在 2-3 秒，对于复杂查询也能在 5 秒内给出回应。

**代码准确性**: 生成的代码通过率超过 85%，远高于行业平均水平。

**建议质量**: 代码优化建议的采纳率达到 70% 以上。

## 对比评测：Shannon AI Hacker vs Cursor

### 代码理解深度

**Cursor**: 主要基于代码语法和结构进行分析
**Shannon AI Hacker**: 能够理解代码的业务逻辑和架构意图

### 个性化程度

**Cursor**: 提供相对标准化的建议
**Shannon AI Hacker**: 深度个性化，真正理解开发者的思维方式

### 学习适应性

**Cursor**: 学习曲线相对平缓，但个性化程度有限
**Shannon AI Hacker**: 具有更强的学习和适应能力

## 使用场景分析：谁最适合 Shannon AI Hacker？

### 个人开发者

对于个人开发者，Shannon AI Hacker 可以：
- 成为编程学习的良师益友
- 帮助建立良好的编程习惯
- 提供个性化的代码优化建议

### 团队协作

在团队环境中，Shannon AI Hacker 能够：
- 统一代码风格和最佳实践
- 协助代码审查和质量控制
- 加速新成员的 onboarding 过程

### 企业级应用

对于企业级开发，它提供了：
- 架构设计建议和优化
- 安全性和性能方面的专业指导
- 与现有开发流程的无缝集成

## 定价策略：性价比分析

Shannon AI Hacker 采用了灵活的定价模式：

**免费版**: 基础功能，适合个人开发者试用
**专业版**: 月付 29 美元，包含高级功能和团队协作
**企业版**: 定制化服务，根据具体需求定价

考虑到它带来的效率提升和代码质量改善，这个定价策略还是相当有竞争力的。

## 未来展望：AI 编程助手的发展方向

Shannon AI Hacker 的出现，让我们看到了 AI 编程助手的未来发展方向：

### 更深层次的代码理解

未来的 AI 助手将不仅仅是代码生成工具，更是能够理解业务逻辑、架构设计的智能伙伴。

### 更个性化的编程体验

每个开发者都将拥有真正理解自己思维方式的"赛博工友"。

### 更智能的协作模式

AI 将在团队协作中发挥更大作用，帮助建立更高效的开发流程。

## 总结：值得一试的"赛博工友"

经过深度评测，我们认为 Shannon AI Hacker 确实是一款值得开发者关注的 AI 编程助手。它不仅在技术能力上表现出色，更重要的是，它真正理解了开发者的需求，提供了一个更加个性化、智能化的编程体验。

虽然它可能还无法完全替代 Cursor 在所有场景下的表现，但在很多方面确实展现出了独特的优势。对于追求高效、个性化编程体验的开发者来说，Shannon AI Hacker 绝对值得一试。

毕竟，在这个 AI 快速发展的时代，拥有一个真正懂你的"赛博工友"，或许就是提升编程效率和代码质量的关键所在。"""
        
        # 尝试访问doocs/md容器的API
        api_url = "http://localhost:8080/api/md2wechat"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            "content": test_markdown,
            "theme": "default"
        }
        
        logging.info(f"正在测试doocs/md容器转换...")
        logging.info(f"API URL: {api_url}")
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        logging.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            
            if result.get('imageUrl') or result.get('data', {}).get('imageUrl'):
                image_url = result.get('imageUrl') or result.get('data', {}).get('imageUrl')
                logging.info(f"✓ doocs/md容器测试成功! 图片URL: {image_url}")
                return True
            else:
                logging.warning(f"doocs/md容器返回格式不同: {result}")
                return False
        else:
            logging.error(f"doocs/md容器请求失败: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        logging.error(f"测试doocs/md容器失败: {e}")
        return False

def test_doocs_md_web():
    """测试doocs/md网页界面"""
    try:
        # 检查网页是否可访问
        response = requests.get("http://localhost:8080", timeout=10)
        if response.status_code == 200:
            logging.info("✓ doocs/md网页界面可正常访问")
            return True
        else:
            logging.error(f"doocs/md网页界面访问失败: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"访问doocs/md网页界面失败: {e}")
        return False

if __name__ == "__main__":
    logging.info("开始测试doocs/md容器...")
    
    # 测试网页界面
    web_success = test_doocs_md_web()
    
    # 测试API转换
    api_success = test_doocs_md_conversion()
    
    if web_success:
        logging.info("✓ doocs/md容器运行正常")
        if api_success:
            logging.info("✓ doocs/md API转换功能可用")
        else:
            logging.warning("⚠ doocs/md API转换功能不可用，但网页界面可用")
            logging.info("可以考虑使用其他方式集成，如浏览器自动化或直接HTML转换")
    else:
        logging.error("✗ doocs/md容器运行异常")