#!/usr/bin/env python3
"""
Markdown转图片的替代方案
使用Python库实现Markdown到图片的转换
"""
import os
import io
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import markdown
from markdown.extensions import codehilite, tables, fenced_code
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarkdownToImageConverter:
    """Markdown转图片转换器"""
    
    def __init__(self):
        # 初始化Markdown解析器
        self.md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'tables',
            'fenced_code',
            'toc'
        ])
        
        # 默认字体配置
        self.font_size = 16
        self.line_height = 24
        self.margin = 40
        self.max_width = 800
        
        # 颜色配置（适合微信公众号）
        self.colors = {
            'background': '#ffffff',
            'text': '#333333',
            'title': '#2c3e50',
            'subtitle': '#34495e',
            'code_bg': '#f8f9fa',
            'code_text': '#e83e8c',
            'quote_border': '#3498db',
            'link': '#3498db'
        }
    
    def convert_markdown_to_html(self, markdown_content):
        """将Markdown转换为HTML"""
        try:
            html = self.md.convert(markdown_content)
            
            # 添加微信公众号友好的CSS样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        font-size: 16px;
                        line-height: 1.6;
                        color: {self.colors['text']};
                        background-color: {self.colors['background']};
                        margin: 0;
                        padding: 20px;
                        max-width: 800px;
                    }}
                    h1 {{
                        font-size: 24px;
                        font-weight: bold;
                        color: {self.colors['title']};
                        margin: 20px 0;
                        border-bottom: 2px solid #eee;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        font-size: 20px;
                        font-weight: bold;
                        color: {self.colors['subtitle']};
                        margin: 20px 0 15px 0;
                    }}
                    h3 {{
                        font-size: 18px;
                        font-weight: bold;
                        color: {self.colors['subtitle']};
                        margin: 15px 0 10px 0;
                    }}
                    p {{
                        margin: 10px 0;
                        text-align: justify;
                    }}
                    code {{
                        background-color: {self.colors['code_bg']};
                        color: {self.colors['code_text']};
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: Consolas, Monaco, 'Courier New', monospace;
                        font-size: 14px;
                    }}
                    pre {{
                        background-color: {self.colors['code_bg']};
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                        margin: 15px 0;
                    }}
                    pre code {{
                        background-color: transparent;
                        color: {self.colors['code_text']};
                        padding: 0;
                    }}
                    blockquote {{
                        border-left: 4px solid {self.colors['quote_border']};
                        margin: 15px 0;
                        padding-left: 20px;
                        color: #666;
                        font-style: italic;
                    }}
                    ul, ol {{
                        margin: 10px 0;
                        padding-left: 30px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                    strong {{
                        font-weight: bold;
                        color: #000;
                    }}
                    em {{
                        font-style: italic;
                    }}
                    a {{
                        color: {self.colors['link']};
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 15px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px 12px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f8f9fa;
                        font-weight: bold;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 15px auto;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            return styled_html
            
        except Exception as e:
            logging.error(f"Markdown转换HTML失败: {e}")
            return None
    
    def create_image_from_html(self, html_content, output_path):
        """将HTML内容转换为图片（简化版）"""
        try:
            # 这里使用一个简化的方法：创建一张白色背景的图片
            # 并在上面绘制文本内容
            
            # 计算图片尺寸（基于内容长度估算）
            lines = html_content.split('\n')
            content_height = len(lines) * self.line_height + 2 * self.margin
            
            # 创建图片
            img = Image.new('RGB', (self.max_width, content_height), self.colors['background'])
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", self.font_size)
                title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", self.font_size + 8)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", self.font_size)
                    title_font = ImageFont.truetype("arial.ttf", self.font_size + 8)
                except:
                    font = ImageFont.load_default()
                    title_font = ImageFont.load_default()
            
            # 绘制内容
            y = self.margin
            for line in lines:
                if line.strip():
                    # 简单的HTML标签处理
                    if line.strip().startswith('<h1>'):
                        text = line.replace('<h1>', '').replace('</h1>', '').strip()
                        draw.text((self.margin, y), text, font=title_font, fill=self.colors['title'])
                        y += self.line_height * 2
                    elif line.strip().startswith('<h2>'):
                        text = line.replace('<h2>', '').replace('</h2>', '').strip()
                        draw.text((self.margin, y), text, font=title_font, fill=self.colors['subtitle'])
                        y += self.line_height * 1.5
                    else:
                        # 移除HTML标签
                        import re
                        clean_text = re.sub('<[^<]+?>', '', line).strip()
                        if clean_text:
                            draw.text((self.margin, y), clean_text, font=font, fill=self.colors['text'])
                            y += self.line_height
                else:
                    y += self.line_height
            
            # 保存图片
            img.save(output_path, 'PNG', quality=95)
            logging.info(f"✓ 图片生成成功: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成图片失败: {e}")
            return False
    
    def convert_markdown_to_image(self, markdown_content, output_path):
        """完整的Markdown转图片流程"""
        try:
            # 1. Markdown转HTML
            html_content = self.convert_markdown_to_html(markdown_content)
            if not html_content:
                return False
            
            # 2. HTML转图片
            success = self.create_image_from_html(html_content, output_path)
            return success
            
        except Exception as e:
            logging.error(f"Markdown转图片失败: {e}")
            return False

def test_converter():
    """测试转换器"""
    converter = MarkdownToImageConverter()
    
    # 测试内容
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
    
    output_path = "/Users/ax/wechat-publisher/test_output.png"
    success = converter.convert_markdown_to_image(test_markdown, output_path)
    
    if success:
        logging.info(f"✓ 测试成功! 图片已保存到: {output_path}")
        return output_path
    else:
        logging.error("✗ 测试失败")
        return None

if __name__ == "__main__":
    test_converter()