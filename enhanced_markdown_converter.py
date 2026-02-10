#!/usr/bin/env python3
"""
增强版Markdown转图片转换器
专为微信公众号优化
"""
import os
import io
import base64
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import markdown
from markdown.extensions import codehilite, tables, fenced_code
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedMarkdownToImageConverter:
    """增强版Markdown转图片转换器"""
    
    def __init__(self):
        # 初始化Markdown解析器
        self.md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'tables',
            'fenced_code',
            'toc'
        ])
        
        # 微信公众号优化配置
        self.font_size = 16
        self.line_height = 28
        self.margin = 50
        self.max_width = 800
        
        # 颜色配置（微信公众号风格）
        self.colors = {
            'background': '#ffffff',
            'text': '#333333',
            'title': '#2c3e50',
            'subtitle': '#34495e',
            'code_bg': '#f8f9fa',
            'code_text': '#e83e8c',
            'quote_border': '#3498db',
            'link': '#3498db',
            'highlight': '#fff3cd',
            'border': '#dee2e6'
        }
        
        # 字体配置
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """加载字体"""
        fonts = {}
        
        # 尝试加载各种系统字体
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "C:/Windows/Fonts/simhei.ttf",  # Windows
            "C:/Windows/Fonts/msyh.ttc",
        ]
        
        # 默认字体
        try:
            fonts['default'] = ImageFont.truetype(font_paths[0], self.font_size)
            fonts['title'] = ImageFont.truetype(font_paths[0], self.font_size + 8)
            fonts['subtitle'] = ImageFont.truetype(font_paths[0], self.font_size + 4)
            fonts['code'] = ImageFont.truetype(font_paths[0], self.font_size - 2)
        except:
            # 回退到默认字体
            fonts['default'] = ImageFont.load_default()
            fonts['title'] = ImageFont.load_default()
            fonts['subtitle'] = ImageFont.load_default()
            fonts['code'] = ImageFont.load_default()
        
        return fonts
    
    def parse_markdown_content(self, markdown_content):
        """解析Markdown内容为结构化数据"""
        lines = markdown_content.split('\n')
        structured_content = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # 标题
            if line.startswith('#'):
                level = len(line.split()[0])
                text = line[level:].strip()
                structured_content.append({
                    'type': 'heading',
                    'level': level,
                    'text': text
                })
            
            # 代码块
            elif line.startswith('```'):
                lang = line[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                structured_content.append({
                    'type': 'code',
                    'language': lang,
                    'content': '\n'.join(code_lines)
                })
            
            # 引用
            elif line.startswith('>'):
                text = line[1:].strip()
                structured_content.append({
                    'type': 'quote',
                    'text': text
                })
            
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    items.append(lines[i][2:].strip())
                    i += 1
                i -= 1  # 回退一行
                
                structured_content.append({
                    'type': 'list',
                    'items': items
                })
            
            # 普通段落
            else:
                paragraph_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '```', '>', '- ', '* ')):
                    paragraph_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # 回退一行
                
                text = ' '.join(paragraph_lines)
                if text:
                    structured_content.append({
                        'type': 'paragraph',
                        'text': text
                    })
            
            i += 1
        
        return structured_content
    
    def calculate_image_size(self, structured_content):
        """计算图片尺寸"""
        height = self.margin * 2  # 上下边距
        
        for item in structured_content:
            if item['type'] == 'heading':
                if item['level'] == 1:
                    height += self.line_height * 2.5
                elif item['level'] == 2:
                    height += self.line_height * 2
                else:
                    height += self.line_height * 1.5
            
            elif item['type'] == 'paragraph':
                # 估算段落行数
                text_length = len(item['text'])
                lines = (text_length // 50) + 1  # 假设每行50个字符
                height += lines * self.line_height
            
            elif item['type'] == 'code':
                code_lines = item['content'].count('\n') + 1
                height += code_lines * (self.line_height - 2) + 20  # 代码块额外边距
            
            elif item['type'] == 'quote':
                height += self.line_height * 1.2
            
            elif item['type'] == 'list':
                height += len(item['items']) * self.line_height
            
            # 添加段落间距
            height += self.line_height * 0.5
        
        return (self.max_width, int(height))
    
    def create_enhanced_image(self, structured_content, output_path):
        """创建增强版图片"""
        try:
            # 计算图片尺寸
            width, height = self.calculate_image_size(structured_content)
            
            # 创建图片
            img = Image.new('RGB', (width, height), self.colors['background'])
            draw = ImageDraw.Draw(img)
            
            # 绘制内容
            y = self.margin
            
            for item in structured_content:
                if y + self.line_height > height - self.margin:
                    break  # 避免超出边界
                
                if item['type'] == 'heading':
                    if item['level'] == 1:
                        font = self.fonts['title']
                        font_size = self.font_size + 8
                        color = self.colors['title']
                        y_offset = self.line_height * 2
                        # 添加下划线
                        text_width = draw.textlength(item['text'], font=font)
                        draw.line([(self.margin, y + y_offset - 5), (self.margin + text_width, y + y_offset - 5)], fill='#eee', width=2)
                    elif item['level'] == 2:
                        font = self.fonts['subtitle']
                        font_size = self.font_size + 4
                        color = self.colors['subtitle']
                        y_offset = self.line_height * 1.5
                    else:
                        font = self.fonts['default']
                        font_size = self.font_size + 2
                        color = self.colors['subtitle']
                        y_offset = self.line_height * 1.2
                    
                    draw.text((self.margin, y), item['text'], font=font, fill=color)
                    y += y_offset
                
                elif item['type'] == 'paragraph':
                    # 文本换行处理
                    text = item['text']
                    max_width = width - 2 * self.margin
                    lines = self.wrap_text(text, self.fonts['default'], max_width, draw)
                    
                    for line in lines:
                        draw.text((self.margin, y), line, font=self.fonts['default'], fill=self.colors['text'])
                        y += self.line_height
                
                elif item['type'] == 'code':
                    # 绘制代码块背景
                    code_lines = item['content'].split('\n')
                    code_height = len(code_lines) * (self.line_height - 2) + 20
                    draw.rectangle([(self.margin - 10, y - 5), (width - self.margin + 10, y + code_height - 5)], 
                                   fill=self.colors['code_bg'], outline=self.colors['border'])
                    
                    # 绘制代码内容
                    for line in code_lines:
                        draw.text((self.margin, y), line, font=self.fonts['code'], fill=self.colors['code_text'])
                        y += self.line_height - 2
                    
                    y += 10  # 代码块后间距
                
                elif item['type'] == 'quote':
                    # 绘制引用边框
                    quote_height = self.line_height * 1.2
                    draw.rectangle([(self.margin - 5, y), (self.margin - 2, y + quote_height)], 
                                   fill=self.colors['quote_border'])
                    
                    # 绘制引用文本
                    draw.text((self.margin + 10, y), item['text'], font=self.fonts['default'], 
                             fill=self.colors['text'])
                    y += quote_height
                
                elif item['type'] == 'list':
                    for i, list_item in enumerate(item['items']):
                        # 绘制列表符号
                        draw.text((self.margin + 20, y), f"• {list_item}", 
                                 font=self.fonts['default'], fill=self.colors['text'])
                        y += self.line_height
                
                # 添加段落间距
                y += self.line_height * 0.3
            
            # 保存图片
            img.save(output_path, 'PNG', quality=95, optimize=True)
            logging.info(f"✓ 增强版图片生成成功: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成增强版图片失败: {e}")
            return False
    
    def wrap_text(self, text, font, max_width, draw):
        """文本换行处理"""
        lines = []
        words = text.split()
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = draw.textlength(word + ' ', font=font)
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def convert_markdown_to_image(self, markdown_content, output_path):
        """完整的Markdown转图片流程"""
        try:
            # 1. 解析Markdown内容
            structured_content = self.parse_markdown_content(markdown_content)
            if not structured_content:
                logging.error("Markdown内容解析失败")
                return False
            
            # 2. 创建增强版图片
            success = self.create_enhanced_image(structured_content, output_path)
            return success
            
        except Exception as e:
            logging.error(f"增强版Markdown转图片失败: {e}")
            return False

def test_enhanced_converter():
    """测试增强版转换器"""
    converter = EnhancedMarkdownToImageConverter()
    
    # 测试内容（类似之前测试的文章）
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
    
    output_path = "/Users/ax/wechat-publisher/enhanced_test_output.png"
    success = converter.convert_markdown_to_image(test_markdown, output_path)
    
    if success:
        logging.info(f"✓ 增强版测试成功! 图片已保存到: {output_path}")
        return output_path
    else:
        logging.error("✗ 增强版测试失败")
        return None

if __name__ == "__main__":
    test_enhanced_converter()