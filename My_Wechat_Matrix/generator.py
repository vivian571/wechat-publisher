#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Matrix Content Generator
自动为多个公众号账号生成个性化内容
"""

import os
import json
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

PROXY_URL = "http://127.0.0.1:3067"  

os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

# 支持多种AI提供商
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not installed. Run: pip install openai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini library not installed. Run: pip install google-generativeai")


class ContentGenerator:
    """内容生成器核心类"""
    
    def __init__(self, config_path: str = "matrix_config.json"):
        """初始化生成器"""
        self.base_dir = Path(__file__).parent
        self.accounts_dir = self.base_dir / "accounts"
        self.templates_dir = self.base_dir / "templates"
        
        # 加载配置
        with open(self.base_dir / config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 加载CSS模板
        css_path = self.templates_dir / "wechat_style.css"
        with open(css_path, 'r', encoding='utf-8') as f:
            self.css_template = f.read()
        
        # 初始化AI客户端
        self.ai_client = self._init_ai_client()
    
    def _init_ai_client(self):
        """初始化AI客户端"""
        provider = self.config.get("ai_provider", "openai")
        
        if provider == "openai" and OPENAI_AVAILABLE:
            api_config = self.config["api_config"]["openai"]
            return OpenAI(
                api_key=api_config["api_key"],
                base_url=api_config.get("base_url", "https://api.openai.com/v1")
            )
        elif provider == "gemini" and GEMINI_AVAILABLE:
            api_config = self.config["api_config"]["gemini"]
            genai.configure(api_key=api_config["api_key"])
            return genai.GenerativeModel(api_config["model"])
        else:
            raise ValueError(f"AI provider '{provider}' not available or not installed")
    
    def load_account_config(self, account_path: Path) -> Dict:
        """加载账号配置"""
        # 读取账号配置
        config_file = account_path / "account_config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            account_config = json.load(f)
        
        # 读取系统提示词
        prompt_file = account_path / "system_prompt.md"
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # 读取风格参考
        style_file = account_path / "style_reference.txt"
        with open(style_file, 'r', encoding='utf-8') as f:
            style_reference = f.read()
        
        return {
            "config": account_config,
            "system_prompt": system_prompt,
            "style_reference": style_reference
        }
    
    def generate_content(self, account_name: str, topic: Optional[str] = None) -> str:
        """为指定账号生成内容"""
        account_path = self.accounts_dir / account_name
        
        if not account_path.exists():
            raise ValueError(f"Account '{account_name}' not found")
        
        # 加载账号配置
        account_data = self.load_account_config(account_path)
        account_config = account_data["config"]
        
        # 检查账号是否启用
        if not account_config.get("enabled", True):
            print(f"⏭️  [{account_config['account_name']}] 账号已禁用，跳过")
            return None
        
        print(f"🧠 [{account_config['account_name']}] 正在思考和写作...")
        
        # 构建提示词
        user_prompt = self._build_user_prompt(account_data, topic)
        
        # 调用AI生成内容
        markdown_content = self._call_ai(
            system_prompt=account_data["system_prompt"],
            user_prompt=user_prompt,
            style_reference=account_data["style_reference"]
        )
        
        # 转换为HTML
        html_content = self._markdown_to_html(markdown_content)
        
        # 保存输出
        output_path = account_path / "output.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ [{account_config['account_name']}] 内容已生成: {output_path}")
        
        return output_path
    
    def _build_user_prompt(self, account_data: Dict, topic: Optional[str]) -> str:
        """构建用户提示词"""
        config = account_data["config"]
        target_words = config.get("target_word_count", 1500)
        
        if topic:
            prompt = f"请写一篇关于「{topic}」的文章，字数控制在{target_words}字左右。"
        else:
            topics = config.get("preferred_topics", [])
            topics_str = "、".join(topics)
            prompt = f"请从以下主题中选择一个写一篇文章：{topics_str}。字数控制在{target_words}字左右。"
        
        prompt += "\n\n请输出为Markdown格式，包含标题、小标题、正文等完整结构。"
        
        return prompt
    
    def _call_ai(self, system_prompt: str, user_prompt: str, style_reference: str) -> str:
        """调用AI生成内容"""
        provider = self.config.get("ai_provider", "openai")
        gen_settings = self.config.get("generation_settings", {})
        
        # 组合完整的系统提示词
        full_system_prompt = f"{system_prompt}\n\n请模仿以下文章的风格和语气：\n\n{style_reference}"
        
        if provider == "openai":
            model = self.config["api_config"]["openai"]["model"]
            response = self.ai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=gen_settings.get("temperature", 0.7),
                max_tokens=gen_settings.get("max_tokens", 2000)
            )
            return response.choices[0].message.content
        
        elif provider == "gemini":
            # Gemini使用不同的API结构
            prompt = f"{full_system_prompt}\n\n{user_prompt}"
            response = self.ai_client.generate_content(
                prompt,
                generation_config={
                    "temperature": gen_settings.get("temperature", 0.7),
                    "max_output_tokens": gen_settings.get("max_tokens", 2000)
    
                },
                request_options={"timeout": 600}  
            )
            return response.text
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """将Markdown转换为纯净的HTML（无样式）"""
        # 使用markdown库转换，支持代码高亮、表格等扩展
        html_body = markdown.markdown(
            markdown_content,
            extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
        )
        
        # 组装完整的HTML文档（不包含CSS样式）
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WeChat Article</title>
</head>
<body>
{html_body}
</body>
</html>"""
        
        return html_template
    
    def generate_all(self, topic: Optional[str] = None):
        """为所有启用的账号生成内容"""
        print(f"\n{'='*60}")
        print(f"🚀 开始批量生成内容 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        generated_count = 0
        
        # 遍历所有账号文件夹
        for account_dir in sorted(self.accounts_dir.iterdir()):
            if account_dir.is_dir():
                try:
                    result = self.generate_content(account_dir.name, topic)
                    if result:
                        generated_count += 1
                except Exception as e:
                    print(f"❌ [{account_dir.name}] 生成失败: {e}")
        
        print(f"\n{'='*60}")
        print(f"✨ 完成！共生成 {generated_count} 篇文章")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Matrix Content Generator")
    parser.add_argument(
        "--account",
        type=str,
        help="指定账号名称（如：Account_A_CrossBorder）"
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="指定文章主题"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="为所有启用的账号生成内容"
    )
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = ContentGenerator()
    
    if args.all:
        # 批量生成
        generator.generate_all(topic=args.topic)
    elif args.account:
        # 单个账号生成
        generator.generate_content(args.account, topic=args.topic)
    else:
        # 默认为所有账号生成
        generator.generate_all(topic=args.topic)


if __name__ == "__main__":
    main()
