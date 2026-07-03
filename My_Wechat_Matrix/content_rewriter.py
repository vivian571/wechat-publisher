#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI驱动的内容改写与优化系统
支持内容扩展、缩减、改写和风格转换
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentRewriter:
    """内容改写器"""
    
    def __init__(self, ai_client=None):
        """初始化改写器"""
        self.ai_client = ai_client
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / "matrix_config.json"
        
        if not ai_client:
            self._init_ai_client()
    
    def _init_ai_client(self):
        """初始化AI客户端"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            provider = config.get("ai_provider", "openai")
            
            if provider == "openai":
                from openai import OpenAI
                api_config = config["api_config"]["openai"]
                self.ai_client = OpenAI(
                    api_key=api_config["api_key"],
                    base_url=api_config.get("base_url", "https://api.openai.com/v1")
                )
            elif provider == "gemini":
                import google.generativeai as genai
                api_config = config["api_config"]["gemini"]
                genai.configure(api_key=api_config["api_key"])
                self.ai_client = genai.GenerativeModel(api_config["model"])
            elif provider == "zhipu":
                from zhipuai import ZhipuAI
                api_config = config["api_config"]["zhipu"]
                self.ai_client = ZhipuAI(api_key=api_config["api_key"])
        except Exception as e:
            logger.warning(f"⚠️ AI客户端初始化失败: {e}")
            self.ai_client = None
    
    def expand_content(self, content: str, target_length: int = None, style: str = None) -> Optional[str]:
        """
        扩展内容
        
        Args:
            content: 原始内容
            target_length: 目标字符长度
            style: 风格（可选）
        
        Returns:
            扩展后的内容
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法进行内容扩展")
            return None
        
        current_length = len(content)
        
        if target_length and current_length >= target_length:
            logger.info(f"ℹ️ 内容已达到目标长度 ({current_length} >= {target_length})")
            return content
        
        # 计算需要增加的内容量
        expand_rate = "30%" if not target_length else f"{int((target_length - current_length) / current_length * 100)}%"
        
        prompt = f"""请扩展以下内容，增加约{expand_rate}的字数。
要求：
1. 保持原意和核心观点
2. 添加相关的实例、数据或解释
3. 增强论证的说服力
4. 保持文章的流畅性和连贯性
{'5. 风格:' + style if style else ''}

原始内容：
{content}

请直接输出扩展后的内容，不需要任何前置说明。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                # OpenAI格式
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=3000
                )
                expanded = response.choices[0].message.content
            else:
                # 其他格式
                response = self.ai_client.complete(prompt)
                expanded = response.get("content", "")
            
            logger.info(f"✅ 内容扩展完成 ({current_length} → {len(expanded)} 字符)")
            return expanded
        
        except Exception as e:
            logger.error(f"❌ 内容扩展失败: {e}")
            return None
    
    def shrink_content(self, content: str, target_length: int = None, keep_key_points: bool = True) -> Optional[str]:
        """
        缩减内容
        
        Args:
            content: 原始内容
            target_length: 目标字符长度
            keep_key_points: 是否保留关键点
        
        Returns:
            缩减后的内容
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法进行内容缩减")
            return None
        
        current_length = len(content)
        
        if target_length and current_length <= target_length:
            logger.info(f"ℹ️ 内容已小于目标长度 ({current_length} <= {target_length})")
            return content
        
        # 计算需要减少的内容量
        shrink_rate = "20%" if not target_length else f"{int((current_length - target_length) / current_length * 100)}%"
        
        prompt = f"""请简化以下内容，缩减约{shrink_rate}的字数。
要求：
1. 保留核心观点和关键信息
2. 删除冗余和不必要的细节
3. 提炼最重要的部分
4. 保持逻辑清晰
5. 易于快速理解

原始内容：
{content}

请直接输出简化后的内容，不需要任何前置说明。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                shrunk = response.choices[0].message.content
            else:
                response = self.ai_client.complete(prompt)
                shrunk = response.get("content", "")
            
            logger.info(f"✅ 内容缩减完成 ({current_length} → {len(shrunk)} 字符)")
            return shrunk
        
        except Exception as e:
            logger.error(f"❌ 内容缩减失败: {e}")
            return None
    
    def rewrite_for_style(self, content: str, source_style: str, target_style: str) -> Optional[str]:
        """
        转换内容风格
        
        Args:
            content: 原始内容
            source_style: 源风格
            target_style: 目标风格
        
        Returns:
            转换后的内容
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法进行风格转换")
            return None
        
        style_mappings = {
            "technical": "技术专业，包含详细的技术细节",
            "casual": "轻松随意，像朋友聊天",
            "formal": "正式严谨，专业学术风格",
            "humorous": "幽默诙谐，包含笑点",
            "emotional": "富有感情，引起共鸣",
            "persuasive": "说服力强，逻辑清晰"
        }
        
        source_desc = style_mappings.get(source_style, source_style)
        target_desc = style_mappings.get(target_style, target_style)
        
        prompt = f"""请将以下内容从"{source_desc}"风格转换为"{target_desc}"风格。
要求：
1. 保留所有重要信息和数据
2. 改变表达方式和措辞
3. 调整句子结构和长度
4. 符合目标风格的特点
5. 保持意思清晰准确

原始内容：
{content}

请直接输出转换后的内容，不需要任何前置说明。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=2500
                )
                rewritten = response.choices[0].message.content
            else:
                response = self.ai_client.complete(prompt)
                rewritten = response.get("content", "")
            
            logger.info(f"✅ 风格转换完成 ({source_style} → {target_style})")
            return rewritten
        
        except Exception as e:
            logger.error(f"❌ 风格转换失败: {e}")
            return None
    
    def generate_variations(self, content: str, num_variations: int = 3) -> Optional[List[str]]:
        """
        生成内容变体（用于A/B测试）
        
        Args:
            content: 原始内容
            num_variations: 变体数量
        
        Returns:
            变体列表
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法生成变体")
            return None
        
        prompt = f"""请基于以下内容生成{num_variations}个不同的表述版本。
要求：
1. 每个版本都保留核心信息
2. 表述方式和重点各不相同
3. 可用于A/B测试
4. 每个版本长度相近
5. 标号为 [版本1]、[版本2] 等

原始内容：
{content}

请按照格式输出各版本。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=3000
                )
                result = response.choices[0].message.content
            else:
                response = self.ai_client.complete(prompt)
                result = response.get("content", "")
            
            # 解析版本
            variations = []
            pattern = r"\[版本\d+\][：:](.*?)(?=\[版本|\Z)"
            matches = re.findall(pattern, result, re.DOTALL)
            
            if matches:
                variations = [m.strip() for m in matches]
            else:
                # 如果没有找到标记，按段落分割
                variations = [v.strip() for v in result.split("\n\n") if v.strip()]
            
            logger.info(f"✅ 生成了{len(variations)}个内容变体")
            return variations[:num_variations]
        
        except Exception as e:
            logger.error(f"❌ 变体生成失败: {e}")
            return None
    
    def extract_key_points(self, content: str, max_points: int = 5) -> Optional[List[str]]:
        """
        提取内容的关键点
        
        Args:
            content: 原始内容
            max_points: 最多关键点数
        
        Returns:
            关键点列表
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法提取关键点")
            return None
        
        prompt = f"""请从以下内容中提取最多{max_points}个关键要点。
要求：
1. 每个要点用数字编号
2. 简洁清晰，不超过一句话
3. 涵盖最重要的信息
4. 按重要程度排序

内容：
{content}

请按格式输出关键点。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000
                )
                result = response.choices[0].message.content
            else:
                response = self.ai_client.complete(prompt)
                result = response.get("content", "")
            
            # 解析要点
            key_points = []
            pattern = r"^\d+[.）:：\s]+(.*?)$"
            for line in result.split("\n"):
                match = re.match(pattern, line.strip())
                if match:
                    point = match.group(1).strip()
                    if point:
                        key_points.append(point)
            
            logger.info(f"✅ 提取了{len(key_points)}个关键点")
            return key_points[:max_points]
        
        except Exception as e:
            logger.error(f"❌ 关键点提取失败: {e}")
            return None
    
    def optimize_title(self, title: str, for_platform: str = "wechat") -> Optional[str]:
        """
        优化标题
        
        Args:
            title: 原始标题
            for_platform: 目标平台
        
        Returns:
            优化后的标题
        """
        if not self.ai_client:
            logger.warning("⚠️ AI客户端不可用，无法优化标题")
            return None
        
        platform_tips = {
            "wechat": "微信公众号（吸引眼球，引发分享）",
            "weibo": "微博（简洁有趣）",
            "xiaohongshu": "小红书（种草风格）",
            "douyin": "抖音（热点相关）"
        }
        
        platform_tip = platform_tips.get(for_platform, "微信公众号")
        
        prompt = f"""请为以下标题生成5个更吸引人的替代版本。
平台：{platform_tip}

原始标题：{title}

要求：
1. 更具吸引力和点击率
2. 符合平台特色
3. 包含关键词
4. 长度控制在15-25个字符
5. 格式为数字编号列表

请直接列出5个版本，不需要额外说明。"""
        
        try:
            if hasattr(self.ai_client, 'chat'):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=500
                )
                result = response.choices[0].message.content
            else:
                response = self.ai_client.complete(prompt)
                result = response.get("content", "")
            
            # 提取第一个建议的标题
            lines = result.strip().split("\n")
            for line in lines:
                match = re.match(r"^\d+[.）:：\s]+(.*?)$", line.strip())
                if match:
                    optimized_title = match.group(1).strip()
                    logger.info(f"✅ 标题优化完成")
                    return optimized_title
            
            # 如果解析失败，返回原标题
            return title
        
        except Exception as e:
            logger.error(f"❌ 标题优化失败: {e}")
            return title
