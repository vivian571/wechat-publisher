#!/usr/bin/env python3
"""
超简热血技术风格Markdown转图片转换器
"""
import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)

class SimpleTechBloodConverter:
    """超简热血技术风格转换器"""
    
    def __init__(self):
        self.colors = {
            'background': '#0c0c0c',
            'text': '#e0e0e0', 
            'title': '#ff4444',
            'code_bg': '#1e1e1e',
            'code_text': '#ffcc00',
            'border': '#333333'
        }
        
        self.font_size = 16
        self.line_height = 28
        self.margin = 40
        self.max_width = 800
        
        # 简单字体
        self.font = ImageFont.load_default()
        self.title_font = self.font
        self.code_font = self.font
    
    def create_simple_tech_image(self, text_content, output_path):
        """创建简单热血技术风格图片"""
        try:
            # 估算高度
            lines = text_content.split('\n')
            height = self.margin * 2 + len(lines) * self.line_height + 100
            
            # 创建图片
            img = Image.new('RGB', (self.max_width, height), self.colors['background'])
            draw = ImageDraw.Draw(img)
            
            # 绘制渐变背景
            for y in range(height):
                ratio = y / height
                r = int(12 + (26 - 12) * ratio)
                g = int(12 + (26 - 12) * ratio)
                b = int(12 + (26 - 12) * ratio)
                draw.line([(0, y), (self.max_width, y)], fill=(r, g, b))
            
            # 重新绘制内容
            y = self.margin
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    y += self.line_height
                    continue
                
                # 标题
                if line.startswith('#'):
                    level = len(line.split()[0])
                    text = line[level:].strip()
                    
                    # 热血红色标题
                    if level == 1:
                        try:
                            title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", self.font_size + 8)
                        except:
                            title_font = self.font
                        
                        # 绘制发光效果
                        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                            draw.text((self.margin + offset[0], y + offset[1]), text, 
                                     font=title_font, fill=(255, 68, 68))
                        
                        draw.text((self.margin, y), text, font=title_font, fill=self.colors['title'])
                        y += self.line_height * 2
                    else:
                        draw.text((self.margin, y), text, font=self.title_font, fill=self.colors['title'])
                        y += self.line_height * 1.5
                
                # 代码块
                elif line.startswith('```') or ('docker' in line.lower() and 'run' in line.lower()):
                    # 绘制代码背景
                    code_lines = [line]
                    if line.startswith('```'):
                        code_lines = ['# Docker 安装命令', 'docker run -d --restart=always -p 3001:3001 louislam/uptime-kuma:1']
                    
                    for code_line in code_lines:
                        draw.rectangle([(self.margin - 10, y - 5), (self.max_width - self.margin + 10, y + self.line_height + 5)], 
                                      fill=self.colors['code_bg'], outline=self.colors['border'])
                        draw.text((self.margin, y), code_line, font=self.code_font, fill=self.colors['code_text'])
                        y += self.line_height
                    
                    y += self.line_height
                
                # 引用
                elif line.startswith('>'):
                    text = line[1:].strip()
                    draw.rectangle([(self.margin - 5, y), (self.margin - 2, y + self.line_height)], 
                                  fill=self.colors['title'])
                    draw.text((self.margin + 10, y), text, font=self.font, fill=self.colors['text'])
                    y += self.line_height * 1.2
                
                # 列表
                elif line.startswith(('- ', '* ')):
                    text = line[2:].strip()
                    draw.text((self.margin + 20, y), '• ' + text, font=self.font, fill=self.colors['text'])
                    y += self.line_height
                
                # 普通文本
                else:
                    # 特殊关键词高亮
                    words = line.split()
                    x = self.margin
                    
                    for word in words:
                        if word in ['**完全免费**', '**自托管**', '**多协议支持**']:
                            # 热血红色高亮
                            clean_word = word.replace('**', '')
                            draw.text((x, y), clean_word, font=self.font, fill=self.colors['title'])
                            x += len(clean_word) * 12
                        elif word in ['$20+', '完全免费']:
                            # 绿色免费标识
                            draw.text((x, y), word, font=self.font, fill='#00ff88')
                            x += len(word) * 12
                        else:
                            draw.text((x, y), word + ' ', font=self.font, fill=self.colors['text'])
                            x += len(word) * 10
                    
                    y += self.line_height
                
                y += self.line_height * 0.3
            
            # 保存图片
            img.save(output_path, 'PNG', quality=95)
            print(f"✅ 热血技术风格图片生成成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return False

def quick_test():
    """快速测试"""
    converter = SimpleTechBloodConverter()
    
    # 热血技术内容
    tech_content = """# 🔥 别再为监控付费了！

**完全免费** **自托管** **多协议支持**

> 开源神器 Uptime Kuma 火了，Pingdom 真的要慌了！

## ⚡ 核心特性

- **完全免费**：零成本，告别昂贵的商业监控服务 $20+ → 完全免费
- **自托管**：数据完全掌控在自己手中
- **多协议支持**：HTTP、TCP、Ping、DNS 全覆盖

## 💻 快速安装

```bash
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

## 🎯 为什么选择？

**传统商业监控** vs **Uptime Kuma**：

- 💰 **成本**：月费 $20+ → **完全免费**
- 🔒 **数据**：第三方托管 → **自托管掌控**
- ⚙️ **灵活性**：功能固定 → **开源可定制**

---

**🔥 热血推荐**：立即部署，让你的服务监控不再花冤枉钱！
"""
    
    output_path = "/Users/ax/wechat-publisher/quick_tech_blood.png"
    success = converter.create_simple_tech_image(tech_content, output_path)
    
    if success:
        file_size = os.path.getsize(output_path)
        print(f"🎉 快速测试成功!")
        print(f"📁 文件: {output_path}")
        print(f"📊 大小: {file_size} 字节")
        return output_path
    else:
        print("❌ 快速测试失败")
        return None

if __name__ == "__main__":
    quick_test()