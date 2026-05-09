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
import re
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

try:
    from zhipuai import ZhipuAI
    ZHIPU_AVAILABLE = True
except ImportError:
    ZHIPU_AVAILABLE = False
    print("⚠️  ZhipuAI library not installed. Run: pip install zhipuai")


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
        
        
        # CSS模板不再需要（已改为纯文本输出）
        self.css_template = ""

        
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
        elif provider == "zhipu" and ZHIPU_AVAILABLE:
            api_config = self.config["api_config"]["zhipu"]
            return ZhipuAI(api_key=api_config["api_key"])
        else:
            raise ValueError(f"AI provider '{provider}' not available or not installed")
    
    def load_account_config(self, account_path: Path) -> Dict:
        """加载账号配置"""
        # 读取账号配置 (修正：改为可选，防止因文件缺失导致崩溃)
        config_file = account_path / "account_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                account_config = json.load(f)
        else:
            account_config = {
                "account_name": account_path.name,
                "enabled": True,
                "target_word_count": 1500
            }
        
        # 读取系统提示词
        prompt_file = account_path / "system_prompt.md"
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # 读取风格参考 (可选)
        style_file = account_path / "style_reference.txt"
        if style_file.exists():
            with open(style_file, 'r', encoding='utf-8') as f:
                style_reference = f.read()
        else:
            style_reference = "专业、客观、理性，具有前瞻性，语言精炼，排版清晰。"
        
        # 加载外部专家角色 (从 agency-agents 仓库)
        agency_rel_path = account_config.get("agency_agent")
        agency_context = ""
        if agency_rel_path:
            agency_context = self._parse_agency_agent(agency_rel_path)
        
        return {
            "config": account_config,
            "system_prompt": system_prompt,
            "style_reference": style_reference,
            "agency_context": agency_context
        }
    
    def _parse_agency_agent(self, agent_rel_path: str) -> str:
        """从 agency-agents 目录解析 Markdown 专家角色"""
        agent_path = self.base_dir / "agency-agents" / agent_rel_path
        if not agent_path.exists():
            print(f"⚠️  未找到 Agency Agent 文件: {agent_path}")
            return ""
        
        try:
            with open(agent_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除 YAML Frontmatter (--- ... ---)
            content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
            
            sections = []
            # 提取 Identity & Memory 部分
            identity_match = re.search(r'#+\s*Identity\s*&\s*Memory(.*?)(?=#+|$)', content, re.IGNORECASE | re.DOTALL)
            if identity_match:
                sections.append(f"【专家身份】\n{identity_match.group(1).strip()}")
            
            # 提取 Critical Rules 部分
            rules_match = re.search(r'#+\s*Critical\s*Rules(.*?)(?=#+|$)', content, re.IGNORECASE | re.DOTALL)
            if rules_match:
                sections.append(f"【核心守则】\n{rules_match.group(1).strip()}")
                
            if not sections:
                return content.strip()[:1500] # 如果没找到特定段落，取前1500字
                
            return "\n\n".join(sections)
        except Exception as e:
            print(f"❌ 解析 Agency Agent 失败 ({agent_rel_path}): {e}")
            return ""
    
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
        text_content = self._call_ai(
            system_prompt=account_data["system_prompt"],
            user_prompt=user_prompt,
            style_reference=account_data["style_reference"],
            agency_context=account_data.get("agency_context", "")
        )
        
        # 保存输出为纯文本
        output_path = account_path / "output.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
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
        
        prompt += "\n\n【严格格式要求】\n1. 必须输出纯文本，严禁使用任何Markdown语法（如#、**、---、```等）。\n2. 第一行必须是文章标题。\n3. 第二行必须是空行。\n4. 第三行开始这一直到最后是正文。\n5. 不要输出“好的”、“以下是文章”等任何对话内容，直接开始输出标题。\n6. 使用空行分段，可以使用emoji（如🌟、📌）和序号（如1.、2.）增强可读性。"
        
        return prompt
    
    def _call_ai(self, system_prompt: str, user_prompt: str, style_reference: str, agency_context: str = "") -> str:
        """调用AI生成内容"""
        provider = self.config.get("ai_provider", "openai")
        gen_settings = self.config.get("generation_settings", {})
        
        # 组合完整的系统提示词
        full_system_prompt = f"{system_prompt}\n\n请模仿以下文章的风格和语气：\n\n{style_reference}"
        
        if agency_context:
            full_system_prompt = f"### 专业级指导原则 (Agency Framework) ###\n{agency_context}\n\n" + full_system_prompt
        
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
        
        elif provider == "zhipu":
            model = self.config["api_config"]["zhipu"].get("model", "glm-4-flash")
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
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    
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
