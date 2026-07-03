#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 图片生成模块
使用 Gemini 或其他 AI API 生成文章配图
"""

import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini library not installed. Run: pip install google-generativeai")


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent / "matrix_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_gemini_api_key() -> str:
    """获取 Gemini API Key"""
    # 1. 优先从环境变量获取
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # 2. 从配置文件获取
    config = load_config()
    if "api_config" in config and "gemini" in config["api_config"]:
        return config["api_config"]["gemini"].get("api_key", "")
    
    return ""


def generate_cover_image_gemini(title: str, output_path: str) -> bool:
    """
    使用 Gemini 生成封面图片
    
    Args:
        title: 文章标题
        output_path: 输出图片路径
        
    Returns:
        是否成功生成
    """
    if not GEMINI_AVAILABLE:
        print("❌ Gemini library not available")
        return False
    
    api_key = get_gemini_api_key()
    if not api_key:
        print("❌ Gemini API Key not found")
        return False
    
    print(f"🎨 正在使用 Gemini 生成封面图片...")
    print(f"   标题: {title[:50]}...")
    
    try:
        genai.configure(api_key=api_key)
        
        # 根据标题判断是否是美食类并添加特定描述
        food_prompt_add = ""
        if any(word in title for word in ["美食", "菜", "汤", "厨", "饭", "食", "味"]):
            food_prompt_add = ", with thick brown sauce, extreme close-up shot, appetizing glossy texture, vibrant colors, fresh garnish, glistening oil glaze, soft indoor lighting, high resolution, macro photography, traditional Chinese home-cooking style."
        
        prompt = f"""Generate a visually appealing, professional cover image for a WeChat article.
        
Article title: {title}

Requirements:
- High quality, vibrant colors
- Food/dish photography style if the title is about food {food_prompt_add}
- Tech/modern style if the title is about technology
- Clean, appetizing, and attractive
- No text in the image
- 16:9 aspect ratio
- Professional lighting
"""
        
        # 尝试使用 Imagen 3
        try:
            model = genai.ImageGenerationModel("imagen-3.0-generate-002")
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9",
            )
            
            if result.images:
                # 保存图片
                image = result.images[0]
                image._pil_image.save(output_path)
                print(f"   ✅ 图片已生成: {output_path}")
                return True
                
        except Exception as e:
            print(f"   ⚠️ Imagen 生成失败: {e}")
            
            # 回退方案：使用 Gemini 的多模态能力描述然后生成
            # 这里需要其他图片生成 API
            
        return False
        
    except Exception as e:
        print(f"   ❌ Gemini 生成失败: {e}")
        return False


def generate_cover_image_pexels(title: str, output_path: str) -> bool:
    """
    使用 Pexels API 搜索相关图片作为封面
    
    Args:
        title: 文章标题
        output_path: 输出图片路径
        
    Returns:
        是否成功
    """
    # 从多个位置读取 API Key
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        config = load_config()
        # 方式1: 顶层 pexels_api_key
        api_key = config.get("pexels_api_key", "")
        # 方式2: api_config.pexels.api_key
        if not api_key and "api_config" in config and "pexels" in config["api_config"]:
            api_key = config["api_config"]["pexels"].get("api_key", "")
    
    if not api_key:
        print("❌ Pexels API Key not found")
        return False
    
    print(f"🔍 正在从 Pexels 搜索封面图片...")
    
    try:
        # 从标题提取关键词
        keywords = extract_keywords(title)
        query = " ".join(keywords[:3])  # 使用前3个关键词
        
        print(f"   关键词: {query}")
        
        headers = {"Authorization": api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=landscape"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                photo = data["photos"][0]
                image_url = photo["src"]["large2x"]  # 高质量图片
                
                # 下载图片
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"   ✅ 图片已下载: {output_path}")
                    return True
        
        print(f"   ⚠️ 未找到合适的图片")
        return False
        
    except Exception as e:
        print(f"   ❌ Pexels 搜索失败: {e}")
        return False


def extract_keywords(title: str) -> list[str]:
    """从标题中提取关键词并转为英文（Pexels需要英文搜索）"""
    # 中文关键词到英文的映射
    keyword_mapping = {
        # AI/科技类
        "AI": "AI technology", "ChatGPT": "AI robot", "人工智能": "artificial intelligence",
        "机器人": "robot", "智能": "smart technology", "科技": "technology",
        "效率": "productivity", "办公": "office work", "自动化": "automation",
        "写作": "writing", "提示词": "AI prompt",
        # 赚钱/副业类
        "赚钱": "money success", "副业": "side hustle", "变现": "business success",
        "收入": "income wealth", "创业": "startup business", "投资": "investment",
        "理财": "finance", "工资": "salary",
        # 美食类
        "美食": "delicious food", "做饭": "cooking", "厨房": "kitchen",
        "下饭": "home cooking", "汤": "soup bowl", "早餐": "breakfast",
        "甜品": "dessert", "火锅": "hot pot", "烧烤": "barbecue",
        "冬天": "winter food", "暖心": "comfort food", "家常": "homemade dish",
        # 养生/健康类
        "养生": "healthy lifestyle", "健康": "health wellness", "医生": "doctor medical",
        "睡眠": "sleep rest", "身体": "body health", "节气": "seasonal health",
        "中医": "traditional medicine", "保健": "wellness", "长寿": "longevity",
        # 通用
        "技巧": "tips tricks", "方法": "method guide", "指南": "guide tips",
    }
    
    # 在标题中匹配关键词
    matched_en = []
    for cn, en in keyword_mapping.items():
        if cn in title:
            matched_en.append(en)
    
    if matched_en:
        return matched_en[:3]  # 最多3个
    
    # 保底：根据标题类型返回通用英文关键词
    if any(word in title for word in ["AI", "ChatGPT", "智能", "科技"]):
        return ["AI technology", "modern office"]
    elif any(word in title for word in ["赚", "钱", "副业", "收入"]):
        return ["business success", "money wealth"]
    elif any(word in title for word in ["吃", "菜", "汤", "做饭", "食"]):
        return ["delicious food", "home cooking"]
    elif any(word in title for word in ["健康", "养生", "医", "睡"]):
        return ["healthy lifestyle", "wellness"]
    else:
        return ["lifestyle", "inspiration"]



def generate_cover_for_article(title: str, account_dir: str) -> str:
    """
    为文章生成封面图片
    
    Args:
        title: 文章标题
        account_dir: 账号目录路径
        
    Returns:
        生成的图片路径，失败返回 None
    """
    output_path = os.path.join(account_dir, "cover_generated.jpg")
    
    # 1. 尝试 Gemini
    if GEMINI_AVAILABLE and get_gemini_api_key():
        if generate_cover_image_gemini(title, output_path):
            return output_path
    
    # 2. 回退到 Pexels
    if generate_cover_image_pexels(title, output_path):
        return output_path
    
    print("❌ 无法生成封面图片")
    return None


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        title = sys.argv[1]
        output_path = "test_cover.jpg"
        if generate_cover_image_pexels(title, output_path):
            print(f"✅ 测试成功: {output_path}")
        else:
            print("❌ 测试失败")
