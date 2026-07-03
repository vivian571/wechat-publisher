#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为微信文章HTML自动添加封面图片（Base64编码）
"""
import sys
import base64
from pathlib import Path
from bs4 import BeautifulSoup

def image_to_base64(image_path: Path) -> str:
    """
    将图片转换为base64编码
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        base64编码的data URL
    """
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 根据文件扩展名确定MIME类型
    ext = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/png')
    
    # 转换为base64
    base64_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{base64_data}"

def add_cover_image(html_file: Path, cover_image_name: str = "cover.png"):
    """
    在文章开头添加封面图片（使用base64编码）
    
    Args:
        html_file: HTML文件路径
        cover_image_name: 封面图片文件名
    """
    print(f"📄 正在处理: {html_file}")
    
    # 确定封面图片完整路径
    cover_image_path = html_file.parent / cover_image_name
    
    if not cover_image_path.exists():
        print(f"❌ 封面图片不存在: {cover_image_path}")
        return
    
    print(f"📸 读取封面图片: {cover_image_path}")
    
    # 转换图片为base64
    print("🔄 正在转换图片为base64编码...")
    base64_url = image_to_base64(cover_image_path)
    print(f"✅ Base64编码完成，长度: {len(base64_url)} 字符")
    
    # 读取HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到js_content div
    content_div = soup.find('div', id='js_content')
    if not content_div:
        print("⚠️  未找到 js_content div")
        return
    
    # 检查是否已有封面图片（删除旧的）
    existing_cover = content_div.find('img', attrs={'alt': 'Shopee选品避坑封面'})
    if existing_cover:
        print("⚠️  检测到旧的封面图片，正在更新...")
        existing_cover.parent.decompose()  # 删除包含图片的p标签
    
    # 找到第一个h1标签
    h1_tag = content_div.find('h1')
    if not h1_tag:
        print("⚠️  未找到 h1 标题标签")
        return
    
    # 创建封面图片元素（使用base64）
    cover_p = soup.new_tag('p', attrs={'style': 'text-align: center; margin: 20px 0;'})
    cover_img = soup.new_tag('img', attrs={
        'src': base64_url,  # 使用base64编码的data URL
        'alt': 'Shopee选品避坑封面',
        'style': 'max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'
    })
    cover_p.append(cover_img)
    
    # 在h1后插入封面图片
    h1_tag.insert_after(cover_p)
    
    # 保存修改后的HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"✅ 封面图片已添加到文章开头")
    print(f"📸 图片路径: {cover_image_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python add_cover_image.py <account_name>")
        print("示例: python add_cover_image.py Account_A_CrossBorder")
        sys.exit(1)
    
    account_name = sys.argv[1]
    base_dir = Path(__file__).parent
    html_file = base_dir / "accounts" / account_name / "output.html"
    
    if not html_file.exists():
        print(f"❌ 文件不存在: {html_file}")
        sys.exit(1)
    
    add_cover_image(html_file)
    print("🎉 完成！")
