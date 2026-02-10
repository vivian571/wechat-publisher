#!/usr/bin/env python3
"""
热血技术风格Markdown转图片转换器
专为编程技术文章设计，采用深色主题、热血配色
"""
import os
import io
import base64
import re
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import markdown
from markdown.extensions import codehilite, tables, fenced_code
import logging

# 导入热血技术风格
from tech_blood_style import TECH_STYLE_CSS, TECH_BLOOD_HTML_TEMPLATE, TECH_BLOOD_SAMPLE_MARKDOWN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TechBloodMarkdownConverter:
    """热血技术风格Markdown转图片转换器"""
    
    def __init__(self):
        # 热血技术风格颜色配置
        self.colors = {
            'background': '#0c0c0c',  # 深黑色背景
            'background_gradient': '#1a1a1a',  # 渐变背景
            'text': '#e0e0e0',  # 主要文本颜色
            'title': '#ff4444',  # 热血红色标题
            'subtitle': '#ff6666',  # 副标题颜色
            'code_bg': '#1e1e1e',  # 代码块背景
            'code_text': '#ffcc00',  # 代码文本颜色
            'quote_border': '#ff4444',  # 引用边框
            'link': '#ff8844',  # 链接颜色
            'highlight': '#ff4444',  # 高亮颜色
            'border': '#333333',  # 边框颜色
            'strong': '#ff6666',  # 强调文本
            'em': '#ffaa88',  # 斜体颜色
            'tag_bg': '#ff4444',  # 标签背景
            'tag_text': '#ffffff',  # 标签文本
        }
        
        # 字体配置（优先使用编程字体）
        self.font_size = 15  # 稍小字体，更适合代码
        self.line_height = 26
        self.margin = 40
        self.max_width = 800
        
        # 加载字体
        self.fonts = self._load_tech_fonts()
        
        # 特殊效果配置
        self.effects = {
            'title_glow': True,
            'code_border': True,
            'gradient_background': True,
            'pulse_animation': False,  # 静态图片不支持动画
        }
    
    def _load_tech_fonts(self):
        """加载技术风格字体"""
        fonts = {}
        
        # 编程字体优先列表
        tech_font_paths = [
            # macOS 编程字体
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.dfont",
            # Linux 编程字体
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/JetBrainsMono-Regular.ttf",
            "/usr/share/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf",
            # Windows 编程字体
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf",
            # 通用备用字体
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/simhei.ttf",
        ]
        
        # 尝试加载字体
        default_font = None
        mono_font = None
        
        for font_path in tech_font_paths:
            try:
                if os.path.exists(font_path):
                    if 'Mono' in font_path or 'mono' in font_path or 'consola' in font_path or 'cour' in font_path:
                        mono_font = ImageFont.truetype(font_path, self.font_size)
                    elif default_font is None:
                        default_font = ImageFont.truetype(font_path, self.font_size)
                    
                    if default_font and mono_font:
                        break
            except Exception as e:
                logging.debug(f"字体加载失败 {font_path}: {e}")
                continue
        
        # 如果都没找到，使用默认字体
        if default_font is None:
            default_font = ImageFont.load_default()
        if mono_font is None:
            mono_font = default_font
        
        # 配置字体
        fonts['default'] = default_font
        fonts['mono'] = mono_font
        fonts['title'] = default_font  # 标题使用相同字体但更大
        fonts['subtitle'] = default_font
        fonts['code'] = mono_font
        
        return fonts
    
    def parse_tech_content(self, markdown_content):
        """解析技术风格内容，支持特殊语法"""
        structured_content = []
        lines = markdown_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # 标题（支持热血风格前缀）
            if line.startswith('#'):
                level = len(line.split()[0])
                text = line[level:].strip()
                
                # 移除热血风格前缀
                if text.startswith(('🔥', '⚡', '🚀', '💻', '🎯')):
                    text = text[2:].strip()
                
                structured_content.append({
                    'type': 'heading',
                    'level': level,
                    'text': text,
                    'icon': self._get_heading_icon(level)
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
                    'language': lang or 'bash',
                    'content': '\n'.join(code_lines)
                })
            
            # 引用（支持热血风格）
            elif line.startswith('>'):
                text = line[1:].strip()
                structured_content.append({
                    'type': 'quote',
                    'text': text,
                    'style': 'tech' if any(word in text.lower() for word in ['hack', '黑客', '热血', '神器']) else 'normal'
                })
            
            # 列表
            elif line.startswith(('- ', '* ', '+ ')):
                items = []
                current_line = i
                while current_line < len(lines) and lines[current_line].strip().startswith(('- ', '* ', '+ ')):
                    item_text = lines[current_line][2:].strip()
                    items.append({
                        'text': item_text,
                        'icon': self._get_list_icon(item_text)
                    })
                    current_line += 1
                
                # 更新索引
                i = current_line - 1
                
                structured_content.append({
                    'type': 'list',
                    'items': items
                })
            
            # 表格
            elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                table_data = []
                headers = [cell.strip() for cell in line.split('|') if cell.strip()]
                table_data.append(headers)
                
                i += 2  # 跳过表头行和分隔行
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                    if row:
                        table_data.append(row)
                    i += 1
                i -= 1
                
                structured_content.append({
                    'type': 'table',
                    'data': table_data
                })
            
            # 标签（HTML风格）
            elif line.startswith('**标签**') or line.startswith('**Tags**'):
                tags = self._parse_tags(line)
                if tags:
                    structured_content.append({
                        'type': 'tags',
                        'tags': tags
                    })
            
            # 普通段落
            else:
                paragraph_lines = []
                while i < len(lines) and lines[i].strip() and not self._is_special_line(lines[i]):
                    paragraph_lines.append(lines[i].strip())
                    i += 1
                i -= 1
                
                text = ' '.join(paragraph_lines)
                if text:
                    # 检查是否包含特殊格式
                    if self._has_emphasis(text) or self._has_code_inline(text):
                        structured_content.append({
                            'type': 'paragraph_enhanced',
                            'text': text
                        })
                    else:
                        structured_content.append({
                            'type': 'paragraph',
                            'text': text
                        })
            
            i += 1
        
        return structured_content
    
    def _get_heading_icon(self, level):
        """获取标题图标"""
        icons = {
            1: '🔥',  # H1 - 火焰
            2: '⚡',  # H2 - 闪电
            3: '🚀',  # H3 - 火箭
        }
        return icons.get(level, '▶')
    
    def _get_list_icon(self, text):
        """获取列表图标"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['免费', '开源', 'open']):
            return '💰'
        elif any(word in text_lower for word in ['支持', '功能', 'feature']):
            return '⚙️'
        elif any(word in text_lower for word in ['快速', 'speed', '性能']):
            return '⚡'
        elif any(word in text_lower for word in ['推荐', '建议', 'tip']):
            return '💡'
        else:
            return '•'
    
    def _parse_tags(self, line):
        """解析标签"""
        # 提取标签内容
        import re
        tag_pattern = r'<span class="tech-tag[^"]*">([^<]+)</span>'
        tags = re.findall(tag_pattern, line)
        return tags
    
    def _is_special_line(self, line):
        """检查是否为特殊行"""
        return (line.strip().startswith(('#', '```', '>', '- ', '* ', '+ ', '|', '**标签**', '**Tags**', '---')) or
                not line.strip())
    
    def _has_emphasis(self, text):
        """检查是否包含强调格式"""
        return '**' in text or '*' in text or '__' in text
    
    def _has_code_inline(self, text):
        """检查是否包含行内代码"""
        return '`' in text
    
    def calculate_tech_image_size(self, structured_content):
        """计算热血技术风格图片尺寸"""
        height = self.margin * 2
        
        for item in structured_content:
            if item['type'] == 'heading':
                if item['level'] == 1:
                    height += self.line_height * 3  # H1 更大间距
                elif item['level'] == 2:
                    height += self.line_height * 2.2
                else:
                    height += self.line_height * 1.8
            
            elif item['type'] == 'paragraph':
                lines = len(item['text']) // 45 + 1  # 技术文章字符密度
                height += lines * self.line_height
            
            elif item['type'] == 'paragraph_enhanced':
                lines = len(item['text']) // 42 + 1
                height += lines * self.line_height
            
            elif item['type'] == 'code':
                code_lines = item['content'].count('\n') + 2
                height += code_lines * (self.line_height - 1) + 25
            
            elif item['type'] == 'quote':
                height += self.line_height * 1.5
            
            elif item['type'] == 'list':
                height += len(item['items']) * self.line_height
            
            elif item['type'] == 'table':
                if item['data']:
                    height += (len(item['data']) + 1) * self.line_height + 20
            
            elif item['type'] == 'tags':
                height += self.line_height + 10
            
            height += self.line_height * 0.4  # 段落间距
        
        return (self.max_width, int(height))
    
    def create_tech_blood_image(self, structured_content, output_path):
        """创建热血技术风格图片"""
        try:
            width, height = self.calculate_tech_image_size(structured_content)
            
            # 创建渐变背景
            img = Image.new('RGB', (width, height), self.colors['background'])
            draw = ImageDraw.Draw(img)
            
            # 绘制渐变背景
            if self.effects['gradient_background']:
                self._draw_gradient_background(draw, width, height)
            
            # 绘制内容
            y = self.margin
            
            for item in structured_content:
                if y + self.line_height > height - self.margin:
                    break
                
                if item['type'] == 'heading':
                    y = self._draw_tech_heading(draw, item, y, width)
                
                elif item['type'] == 'paragraph':
                    y = self._draw_tech_paragraph(draw, item, y, width)
                
                elif item['type'] == 'paragraph_enhanced':
                    y = self._draw_enhanced_paragraph(draw, item, y, width)
                
                elif item['type'] == 'code':
                    y = self._draw_tech_code_block(draw, item, y, width)
                
                elif item['type'] == 'quote':
                    y = self._draw_tech_quote(draw, item, y, width)
                
                elif item['type'] == 'list':
                    y = self._draw_tech_list(draw, item, y, width)
                
                elif item['type'] == 'table':
                    y = self._draw_tech_table(draw, item, y, width)
                
                elif item['type'] == 'tags':
                    y = self._draw_tech_tags(draw, item, y, width)
                
                y += self.line_height * 0.4  # 段落间距
            
            # 保存图片
            img.save(output_path, 'PNG', quality=95, optimize=True)
            logging.info(f"✓ 热血技术风格图片生成成功: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成热血技术风格图片失败: {e}")
            return False
    
    def _draw_gradient_background(self, draw, width, height):
        """绘制渐变背景"""
        # 简单的渐变效果
        for y in range(height):
            ratio = y / height
            r = int(12 + (26 - 12) * ratio)
            g = int(12 + (26 - 12) * ratio)
            b = int(12 + (26 - 12) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _draw_tech_heading(self, draw, item, y, width):
        """绘制技术风格标题"""
        text = item['text']
        level = item['level']
        
        if level == 1:
            # H1 - 热血红色大标题，带发光效果
            font_size = self.font_size + 12
            try:
                title_font = ImageFont.truetype(self.fonts['default'].path, font_size)
            except:
                title_font = self.fonts['default']
            
            color = self.colors['title']
            
            # 绘制发光效果（多层阴影）
            if self.effects['title_glow']:
                for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                    draw.text((self.margin + offset[0], y + offset[1]), text, 
                             font=title_font, fill=(255, 68, 68, 50))
            
            # 绘制主标题
            draw.text((self.margin, y), text, font=title_font, fill=color)
            
            # 绘制下划线
            text_width = draw.textlength(text, font=title_font)
            draw.line([(self.margin, y + font_size + 5), 
                      (self.margin + text_width, y + font_size + 5)], 
                     fill=self.colors['title'], width=3)
            
            return y + font_size + 25
        
        elif level == 2:
            # H2 - 副标题，带图标
            font_size = self.font_size + 6
            try:
                subtitle_font = ImageFont.truetype(self.fonts['default'].path, font_size)
            except:
                subtitle_font = self.fonts['default']
            
            # 绘制图标
            icon = item.get('icon', '▶')
            draw.text((self.margin - 20, y), icon, font=subtitle_font, 
                     fill=self.colors['subtitle'])
            
            # 绘制标题文本
            draw.text((self.margin, y), text, font=subtitle_font, 
                     fill=self.colors['subtitle'])
            
            # 绘制背景条
            text_width = draw.textlength(text, font=subtitle_font)
            draw.rectangle([(self.margin - 5, y - 3), 
                           (self.margin + text_width + 5, y + font_size + 3)], 
                          fill=(255, 68, 68, 30), outline=self.colors['subtitle'])
            
            return y + font_size + 15
        
        else:
            # H3 及其他
            font_size = self.font_size + 3
            try:
                h3_font = ImageFont.truetype(self.fonts['default'].path, font_size)
            except:
                h3_font = self.fonts['default']
            
            draw.text((self.margin, y), text, font=h3_font, 
                     fill=self.colors['subtitle'])
            
            return y + font_size + 12
    
    def _draw_tech_paragraph(self, draw, item, y, width):
        """绘制技术风格段落"""
        text = item['text']
        max_width = width - 2 * self.margin
        
        # 文本换行
        lines = self._wrap_tech_text(text, self.fonts['default'], max_width, draw)
        
        for line in lines:
            draw.text((self.margin, y), line, font=self.fonts['default'], 
                     fill=self.colors['text'])
            y += self.line_height
        
        return y
    
    def _draw_enhanced_paragraph(self, draw, item, y, width):
        """绘制增强段落（支持行内代码和强调）"""
        text = item['text']
        max_width = width - 2 * self.margin
        
        # 解析增强文本
        segments = self._parse_enhanced_text(text)
        
        current_x = self.margin
        current_line = []
        current_width = 0
        line_start_y = y
        
        for segment in segments:
            segment_text = segment['text']
            segment_type = segment['type']
            
            # 计算文本宽度
            if segment_type == 'code':
                font = self.fonts['code']
                color = self.colors['code_text']
                bg_color = self.colors['code_bg']
            elif segment_type == 'strong':
                try:
                    font = ImageFont.truetype(self.fonts['default'].path, self.font_size + 1)
                except:
                    font = self.fonts['default']
                color = self.colors['strong']
            elif segment_type == 'em':
                color = self.colors['em']
                font = self.fonts['default']
            else:
                font = self.fonts['default']
                color = self.colors['text']
            
            # 简单的单行处理（实际应该处理换行）
            draw.text((current_x, line_start_y), segment_text, font=font, fill=color)
            
            # 绘制代码背景
            if segment_type == 'code':
                text_width = draw.textlength(segment_text, font=font)
                draw.rectangle([(current_x - 2, line_start_y - 1), 
                               (current_x + text_width + 2, line_start_y + self.font_size + 1)], 
                              fill=bg_color, outline=self.colors['border'])
                draw.text((current_x, line_start_y), segment_text, font=font, fill=color)
            
            current_x += draw.textlength(segment_text, font=font) + 3
        
        return y + self.line_height
    
    def _draw_tech_code_block(self, draw, item, y, width):
        """绘制技术风格代码块"""
        content = item['content']
        language = item['language']
        
        code_lines = content.split('\n')
        code_height = len(code_lines) * (self.line_height - 2) + 20
        
        # 绘制代码块背景
        draw.rectangle([(self.margin - 10, y - 5), 
                       (width - self.margin + 10, y + code_height - 5)], 
                      fill=self.colors['code_bg'], outline=self.colors['highlight'])
        
        # 绘制语言标签
        if language:
            lang_text = f" {language.upper()} "
            lang_width = draw.textlength(lang_text, font=self.fonts['code'])
            draw.rectangle([(self.margin - 5, y - 15), 
                           (self.margin + lang_width - 5, y - 2)], 
                          fill=self.colors['highlight'], outline=self.colors['highlight'])
            draw.text((self.margin - 3, y - 13), lang_text, font=self.fonts['code'], 
                     fill=self.colors['background'])
        
        # 绘制代码内容
        for j, line in enumerate(code_lines):
            # 简单的语法高亮（bash/python 关键词）
            line_color = self._get_code_color(line, language)
            draw.text((self.margin, y + 10 + j * (self.line_height - 2)), line, 
                     font=self.fonts['code'], fill=line_color)
        
        return y + code_height + 10
    
    def _get_code_color(self, line, language):
        """获取代码行颜色（简单的高亮）"""
        if not line.strip():
            return self.colors['text']
        
        line_lower = line.lower().strip()
        
        # Bash 关键词
        bash_keywords = ['if', 'then', 'else', 'fi', 'for', 'do', 'done', 'while', 'function']
        # Python 关键词  
        python_keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except']
        
        keywords = bash_keywords if language == 'bash' else python_keywords
        
        # 检查是否包含关键词
        for keyword in keywords:
            if keyword in line_lower and len(line_lower.split()[0]) < 10:
                return '#00ff88'  # 绿色关键词
        
        # 注释
        if line.strip().startswith('#'):
            return '#888888'  # 灰色注释
        
        # 字符串
        if any(line.count(char) % 2 == 1 for char in ['"', "'"]):
            return '#ff8800'  # 橙色字符串
        
        return self.colors['code_text']
    
    def _draw_tech_quote(self, draw, item, y, width):
        """绘制技术风格引用"""
        text = item['text']
        style = item.get('style', 'normal')
        
        # 绘制引用边框
        quote_height = self.line_height * 1.5
        border_color = self.colors['quote_border']
        
        draw.rectangle([(self.margin - 5, y), (self.margin - 2, y + quote_height)], 
                      fill=border_color)
        
        # 绘制引用背景
        draw.rectangle([(self.margin + 5, y), (width - self.margin, y + quote_height)], 
                      fill=(255, 68, 68, 20), outline=border_color)
        
        # 特殊风格引用
        if style == 'tech':
            # 添加特殊图标
            draw.text((self.margin + 10, y + 5), '💡', font=self.fonts['default'], 
                     fill=self.colors['highlight'])
            text_x = self.margin + 35
        else:
            text_x = self.margin + 15
        
        # 绘制引用文本
        draw.text((text_x, y + 10), text, font=self.fonts['default'], 
                 fill=self.colors['em'])
        
        return y + quote_height + 15
    
    def _draw_tech_list(self, draw, item, y, width):
        """绘制技术风格列表"""
        for list_item in item['items']:
            icon = list_item.get('icon', '•')
            text = list_item['text']
            
            # 绘制图标
            draw.text((self.margin + 10, y), icon, font=self.fonts['default'], 
                     fill=self.colors['highlight'])
            
            # 绘制列表项文本
            draw.text((self.margin + 35, y), text, font=self.fonts['default'], 
                     fill=self.colors['text'])
            
            y += self.line_height
        
        return y
    
    def _draw_tech_table(self, draw, item, y, width):
        """绘制技术风格表格"""
        if not item['data']:
            return y
        
        table_data = item['data']
        row_height = self.line_height
        col_width = (width - 2 * self.margin - 40) // len(table_data[0])  # 平均分配列宽
        
        # 绘制表头
        headers = table_data[0]
        for j, header in enumerate(headers):
            x = self.margin + 20 + j * col_width
            
            # 绘制表头背景
            draw.rectangle([(x - 5, y - 3), (x + col_width - 10, y + row_height + 3)], 
                          fill=self.colors['highlight'], outline=self.colors['border'])
            
            # 绘制表头文本
            draw.text((x, y), header, font=self.fonts['default'], 
                     fill=self.colors['background'])
        
        y += row_height + 5
        
        # 绘制数据行
        for row in table_data[1:]:
            for j, cell in enumerate(row):
                if j < len(headers):  # 避免越界
                    x = self.margin + 20 + j * col_width
                    
                    # 绘制单元格背景
                    bg_color = (30, 30, 30) if (row[0] == row[0]) else (40, 20, 20)  # 简单的交替色
                    draw.rectangle([(x - 5, y - 2), (x + col_width - 10, y + row_height + 2)], 
                                  fill=bg_color, outline=self.colors['border'])
                    
                    # 绘制单元格文本
                    draw.text((x, y), cell, font=self.fonts['default'], 
                             fill=self.colors['text'])
            
            y += row_height
        
        return y + 15
    
    def _draw_tech_tags(self, draw, item, y, width):
        """绘制技术风格标签"""
        tags = item['tags']
        x = self.margin
        
        for tag in tags:
            tag_text = f" {tag} "
            tag_width = draw.textlength(tag_text, font=self.fonts['code'])
            
            # 绘制标签背景
            draw.rectangle([(x - 3, y - 2), (x + tag_width + 3, y + self.line_height + 2)], 
                          fill=self.colors['highlight'], outline=self.colors['highlight'])
            
            # 绘制标签文本
            draw.text((x, y), tag_text, font=self.fonts['code'], 
                     fill=self.colors['tag_text'])
            
            x += tag_width + 15
        
        return y + self.line_height + 10
    
    def _wrap_tech_text(self, text, font, max_width, draw):
        """技术风格文本换行"""
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
    
    def _parse_enhanced_text(self, text):
        """解析增强文本（支持行内格式）"""
        segments = []
        
        # 简单的解析逻辑（实际需要更复杂的解析）
        import re
        
        # 处理行内代码
        code_pattern = r'`([^`]+)`'
        text = re.sub(code_pattern, lambda m: f'CODE:{m.group(1)}:CODE', text)
        
        # 处理强调
        strong_pattern = r'\*\*([^*]+)\*\*'
        text = re.sub(strong_pattern, lambda m: f'STRONG:{m.group(1)}:STRONG', text)
        
        em_pattern = r'\*([^*]+)\*'
        text = re.sub(em_pattern, lambda m: f'EM:{m.group(1)}:EM', text)
        
        # 分割并创建段
        parts = re.split(r'(CODE:[^:]+:CODE|STRONG:[^:]+:STRONG|EM:[^:]+:EM)', text)
        
        for part in parts:
            if part.startswith('CODE:'):
                segments.append({
                    'type': 'code',
                    'text': part[5:-5]
                })
            elif part.startswith('STRONG:'):
                segments.append({
                    'type': 'strong',
                    'text': part[7:-7]
                })
            elif part.startswith('EM:'):
                segments.append({
                    'type': 'em',
                    'text': part[3:-3]
                })
            elif part.strip():
                segments.append({
                    'type': 'normal',
                    'text': part
                })
        
        return segments
    
    def convert_tech_markdown_to_image(self, markdown_content, output_path):
        """完整的热血技术风格Markdown转图片流程"""
        try:
            # 1. 解析技术风格内容
            structured_content = self.parse_tech_content(markdown_content)
            if not structured_content:
                logging.error("技术风格内容解析失败")
                return False
            
            # 2. 创建热血技术风格图片
            success = self.create_tech_blood_image(structured_content, output_path)
            return success
            
        except Exception as e:
            logging.error(f"热血技术风格Markdown转图片失败: {e}")
            return False

def test_tech_blood_converter():
    """测试热血技术风格转换器"""
    converter = TechBloodMarkdownConverter()
    
    # 使用热血技术风格示例内容
    test_markdown = TECH_BLOOD_SAMPLE_MARKDOWN
    
    output_path = "/Users/ax/wechat-publisher/tech_blood_test_output.png"
    success = converter.convert_tech_markdown_to_image(test_markdown, output_path)
    
    if success:
        logging.info(f"✓ 热血技术风格测试成功! 图片已保存到: {output_path}")
        return output_path
    else:
        logging.error("✗ 热血技术风格测试失败")
        return None

if __name__ == "__main__":
    test_tech_blood_converter()