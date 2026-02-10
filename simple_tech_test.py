#!/usr/bin/env python3
"""
热血技术风格转换器 - 简化测试版本
"""
import os
import sys
sys.path.append('/Users/ax/wechat-publisher')

from tech_blood_converter import TechBloodMarkdownConverter
import logging

logging.basicConfig(level=logging.INFO)

def simple_test():
    """简化测试"""
    print("🚀 开始热血技术风格测试")
    
    converter = TechBloodMarkdownConverter()
    
    # 简化测试内容
    simple_markdown = """# 🔥 别再为监控付费了！

**开源神器 Uptime Kuma 火了**

> 完全免费的监控解决方案

## ⚡ 核心特性

- **完全免费**：零成本，告别昂贵的商业监控
- **自托管**：数据完全掌控在自己手中  
- **多协议支持**：HTTP、TCP、Ping、DNS 全覆盖

## 💻 快速安装

```bash
# 使用 Docker 一键安装
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

## 🎯 为什么选择？

**传统商业监控** vs **Uptime Kuma**：

- 💰 **成本**：月费 $20+ → **完全免费**
- 🔒 **数据**：第三方托管 → **自托管掌控**

---

**🔥 热血推荐**：立即部署，让你的监控不再花冤枉钱！
"""
    
    output_path = "/Users/ax/wechat-publisher/simple_tech_blood_test.png"
    
    try:
        success = converter.convert_tech_markdown_to_image(simple_markdown, output_path)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ 热血技术风格测试成功!")
            print(f"📁 图片已保存: {output_path}")
            print(f"📊 文件大小: {file_size} 字节")
            return True
        else:
            print("❌ 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 热血技术风格转换器已就绪！")
        print("现在可以更新本地md2服务使用新的热血风格了")