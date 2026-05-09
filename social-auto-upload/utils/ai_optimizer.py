# -*- coding: utf-8 -*-
"""
AI 内容优化器模块
支持多个 AI 服务提供商：OpenAI、Claude、DeepSeek、智谱 AI
用于优化视频标题和生成平台特定的标签
"""

import os
import json
from typing import Dict, List, Optional
from enum import Enum


class AIProvider(Enum):
    """AI 服务提供商枚举"""
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    ZHIPU = "zhipu"


class PlatformType(Enum):
    """支持的平台类型"""
    DOUYIN = "douyin"
    BILIBILI = "bilibili"
    XIAOHONGSHU = "xiaohongshu"
    KUAISHOU = "kuaishou"
    TIKTOK = "tiktok"
    TENCENT = "tencent"
    BAIJIAHAO = "baijiahao"


# 平台特定的优化策略提示词
PLATFORM_PROMPTS = {
    PlatformType.DOUYIN.value: {
        "title_style": "简短有力、制造悬念、使用数字和疑问句，长度控制在 20 字以内",
        "tag_style": "热门话题、垂类标签、情感共鸣类标签，3-5 个",
        "examples": "例如：'90% 的人都不知道的技巧'、'3 分钟学会这个方法'",
    },
    PlatformType.BILIBILI.value: {
        "title_style": "详细描述、突出干货、可以较长，适合添加【】符号强调重点",
        "tag_style": "专业领域标签、UP主个人标签、内容分类标签，5-8 个",
        "examples": "例如：'【深度解析】Python 自动化完整教程'、'保姆级教程！从零开始学编程'",
    },
    PlatformType.XIAOHONGSHU.value: {
        "title_style": "生活化、真实感、使用 emoji、制造共鸣，长度 15-25 字",
        "tag_style": "生活方式标签、场景标签、情绪标签，3-5 个",
        "examples": "例如：'姐妹们！这个方法真的绝了✨'、'亲测有效的省钱攻略💰'",
    },
    PlatformType.KUAISHOU.value: {
        "title_style": "接地气、直白、突出实用性，长度 15-20 字",
        "tag_style": "生活实用类标签、地域标签、人群标签，3-5 个",
        "examples": "例如：'老铁们，这招真管用！'、'学会这个能省不少钱'",
    },
    PlatformType.TIKTOK.value: {
        "title_style": "英文或双语、简洁有趣、使用 hashtag，长度控制在 100 字符以内",
        "tag_style": "trending hashtags、niche tags、location tags，5-10 个",
        "examples": "例如：'You won't believe this trick! 🤯'、'Life hack everyone needs to know'",
    },
    PlatformType.TENCENT.value: {
        "title_style": "正式、清晰、突出价值，长度 15-30 字",
        "tag_style": "内容分类标签、行业标签、功能标签，3-5 个",
        "examples": "例如：'微信视频号运营完整指南'、'如何提升视频播放量'",
    },
    PlatformType.BAIJIAHAO.value: {
        "title_style": "新闻化、权威感、突出信息点，长度 20-30 字",
        "tag_style": "新闻分类标签、热点标签、领域标签，3-5 个",
        "examples": "例如：'最新研究发现：这个方法效果显著'、'专家解读：行业发展新趋势'",
    },
}


class AIContentOptimizer:
    """AI 内容优化器"""

    def __init__(
        self,
        provider: str = "openai",
        api_key: str = "",
        model: str = "",
        base_url: str = "",
    ):
        """
        初始化 AI 内容优化器

        Args:
            provider: AI 服务提供商 (openai/claude/deepseek/zhipu)
            api_key: API 密钥
            model: 模型名称（可选，使用默认模型）
            base_url: API 基础 URL（可选，用于自定义端点）
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url

        # 设置默认模型
        if not model:
            model = self._get_default_model()
        self.model = model

        # 初始化客户端
        self.client = self._init_client()

    def _get_default_model(self) -> str:
        """获取默认模型"""
        default_models = {
            AIProvider.OPENAI.value: "gpt-4o-mini",
            AIProvider.CLAUDE.value: "claude-3-5-sonnet-20241022",
            AIProvider.DEEPSEEK.value: "deepseek-chat",
            AIProvider.ZHIPU.value: "glm-4-flash",
        }
        return default_models.get(self.provider, "gpt-4o-mini")

    def _init_client(self):
        """初始化 AI 客户端"""
        if self.provider == AIProvider.OPENAI.value:
            from openai import OpenAI
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else None,
            )
        elif self.provider == AIProvider.CLAUDE.value:
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        elif self.provider == AIProvider.DEEPSEEK.value:
            from openai import OpenAI
            # DeepSeek 使用 OpenAI 兼容接口
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else "https://api.deepseek.com",
            )
        elif self.provider == AIProvider.ZHIPU.value:
            from openai import OpenAI
            # 智谱 AI 使用 OpenAI 兼容接口
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else "https://open.bigmodel.cn/api/paas/v4/",
            )
        else:
            raise ValueError(f"不支持的 AI 服务提供商: {self.provider}")

    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用 AI 服务
        """
        if not self.api_key:
            # 模拟模式：如果没有 API Key，返回带标记的原始信息用于演示
            if "优化标题" in system_prompt:
                # 从 user_prompt 中提取原始标题
                original = user_prompt.split("原始标题：")[-1].strip()
                return f"[AI 模拟优化] {original} - 爆款必看！"
            elif "生成高质量的标签" in system_prompt:
                return "AI标签1\nAI标签2\nAI标签3"
            return "AI 模拟响应"

        try:
            if self.provider == AIProvider.CLAUDE.value:
                # Claude 使用不同的 API 格式
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text
            else:
                # OpenAI 兼容格式（OpenAI、DeepSeek、智谱）
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"AI 调用失败: {e}")
            return ""

    def optimize_title(
        self,
        original_title: str,
        platform: str,
        video_description: str = "",
    ) -> str:
        """
        优化视频标题

        Args:
            original_title: 原始标题
            platform: 目标平台
            video_description: 视频描述（可选）

        Returns:
            优化后的标题
        """
        platform_info = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS[PlatformType.DOUYIN.value])

        system_prompt = f"""你是一个专业的短视频内容运营专家，擅长为不同平台优化视频标题。
你的任务是根据平台特点，将原始标题优化为更吸引人、更符合平台算法偏好的标题。

平台：{platform}
标题风格要求：{platform_info['title_style']}
参考示例：{platform_info['examples']}

注意事项：
1. 保持原始标题的核心信息
2. 使用平台用户熟悉的语言风格
3. 突出视频的价值点和吸引力
4. 只返回优化后的标题，不要有其他解释"""

        user_prompt = f"""原始标题：{original_title}"""
        if video_description:
            user_prompt += f"\n视频描述：{video_description}"

        optimized_title = self._call_ai(system_prompt, user_prompt)
        return optimized_title.strip() if optimized_title else original_title

    def generate_hashtags(
        self,
        title: str,
        platform: str,
        max_tags: int = 5,
        video_description: str = "",
    ) -> List[str]:
        """
        生成平台特定的标签

        Args:
            title: 视频标题
            platform: 目标平台
            max_tags: 最大标签数量
            video_description: 视频描述（可选）

        Returns:
            标签列表
        """
        platform_info = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS[PlatformType.DOUYIN.value])

        system_prompt = f"""你是一个专业的短视频内容运营专家，擅长为不同平台生成高质量的标签。
你的任务是根据视频标题和平台特点，生成最合适的标签。

平台：{platform}
标签风格要求：{platform_info['tag_style']}

注意事项：
1. 标签要与视频内容高度相关
2. 包含热门话题标签和垂类标签
3. 标签要简洁明了，易于搜索
4. 只返回标签列表，每个标签一行，不要有 # 符号和其他解释
5. 最多返回 {max_tags} 个标签"""

        user_prompt = f"""视频标题：{title}"""
        if video_description:
            user_prompt += f"\n视频描述：{video_description}"

        tags_text = self._call_ai(system_prompt, user_prompt)
        if not tags_text:
            return []

        # 解析标签
        tags = [tag.strip().replace("#", "") for tag in tags_text.split("\n") if tag.strip()]
        return tags[:max_tags]

    def optimize_content(
        self,
        original_title: str,
        platform: str,
        video_description: str = "",
        max_tags: int = 5,
    ) -> Dict[str, any]:
        """
        一次性优化标题和生成标签

        Args:
            original_title: 原始标题
            platform: 目标平台
            video_description: 视频描述（可选）
            max_tags: 最大标签数量

        Returns:
            包含优化后标题和标签的字典
        """
        optimized_title = self.optimize_title(original_title, platform, video_description)
        hashtags = self.generate_hashtags(optimized_title, platform, max_tags, video_description)

        return {
            "original_title": original_title,
            "title": optimized_title,
            "tags": hashtags,
            "platform": platform,
        }


# 便捷函数：从配置文件创建优化器
def create_optimizer_from_config(config_dict: Dict) -> Optional[AIContentOptimizer]:
    """
    从配置字典创建优化器

    Args:
        config_dict: 配置字典，应包含以下键：
            - AI_OPTIMIZER_ENABLED: 是否启用
            - AI_PROVIDER: 服务提供商
            - AI_API_KEY: API 密钥
            - AI_MODEL: 模型名称（可选）
            - AI_BASE_URL: 基础 URL（可选）

    Returns:
        AIContentOptimizer 实例，如果未启用则返回 None
    """
    if not config_dict.get("AI_OPTIMIZER_ENABLED", False):
        return None

    provider = config_dict.get("AI_PROVIDER", "openai")
    api_key = config_dict.get("AI_API_KEY", "")
    model = config_dict.get("AI_MODEL", "")
    base_url = config_dict.get("AI_BASE_URL", "")

    if not api_key:
        print("💡 提示：AI_API_KEY 未配置，将进入 AI 模拟演示模式")
        # 允许创建，但会进入模拟逻辑
        return AIContentOptimizer(
            provider=provider,
            api_key="",
            model=model,
            base_url=base_url,
        )

    try:
        return AIContentOptimizer(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except Exception as e:
        print(f"创建 AI 优化器失败: {e}")
        return None


if __name__ == "__main__":
    # 测试代码
    print("AI 内容优化器模块加载成功！")
    print("\n支持的平台：")
    for platform in PlatformType:
        print(f"  - {platform.value}")
    print("\n支持的 AI 服务提供商：")
    for provider in AIProvider:
        print(f"  - {provider.value}")
