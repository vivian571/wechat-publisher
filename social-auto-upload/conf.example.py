from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
XHS_SERVER = "http://127.0.0.1:11901"
LOCAL_CHROME_PATH = ""   # change me necessary！ for example C:/Program Files/Google/Chrome/Application/chrome.exe
LOCAL_CHROME_HEADLESS = False

# ==============================================================================
# AI 内容优化配置
# ==============================================================================
AI_OPTIMIZER_ENABLED = False
# AI 提供商: openai, claude, deepseek, zhipu
AI_PROVIDER = "openai"
AI_API_KEY = ""
# 模型名称 (留空使用默认)
# OpenAI: gpt-4o-mini
# Claude: claude-3-5-sonnet-20241022
# DeepSeek: deepseek-chat
# Zhipu: glm-4-flash
AI_MODEL = ""
AI_BASE_URL = ""  # 自定义 API 端点 (例如 https://api.deepseek.com)

# ==============================================================================
# 封面生成配置
# ==============================================================================
COVER_GENERATOR_ENABLED = False
FFMPEG_PATH = "ffmpeg"  # 确保 ffmpeg 已添加到系统环境变量
COVER_STYLE = "default"  # default, modern, minimal

# ==============================================================================
# 矩阵联动配置
# ==============================================================================
MATRIX_BRIDGE_ENABLED = False
WECHAT_MATRIX_DIR = r"f:\公众号写作\My_Wechat_Matrix"
UPLOAD_QUEUE_DIR = str(BASE_DIR / "videos")

# ==============================================================================
# 视频去重与防风控配置 (Magic Edit)
# ==============================================================================
MAGIC_EDIT_ENABLED = False
# 去重配置选项
MAGIC_EDIT_CONFIG = {
    'crop': True,       # 随机裁剪 1-2%
    'scale': True,      # 缩放回原大小
    'color': True,      # 色调微调
    'flip': False,      # 水平镜像（慎用，某些内容不适合）
    'speed': True,      # 速度微调 (99.9%-100.1%)
    'metadata': True    # 清理元数据
}

# ============ AI 内容优化配置 ============
# 是否启用 AI 标题和标签优化
AI_OPTIMIZER_ENABLED = False

# AI 提供商选择: "openai" / "claude" / "deepseek" / "zhipu"
AI_PROVIDER = "openai"

# API 配置
AI_API_KEY = ""  # 必填：你的 API 密钥
AI_MODEL = ""    # 可选：模型名称（留空使用默认模型）
AI_BASE_URL = ""  # 可选：自定义 API 端点

# 各提供商的默认模型：
# OpenAI: gpt-4o-mini
# Claude: claude-3-5-sonnet-20241022
# DeepSeek: deepseek-chat
# 智谱 AI: glm-4-flash

# ============ 封面生成配置 ============
# 是否启用自动封面生成
COVER_GENERATOR_ENABLED = False

# FFmpeg 可执行文件路径（如果在 PATH 中可留空）
FFMPEG_PATH = "ffmpeg"

# 封面样式：default / modern / minimal
COVER_STYLE = "default"

# ============ 矩阵联动配置 ============
# 是否启用与 My_Wechat_Matrix 的联动
MATRIX_BRIDGE_ENABLED = False

# My_Wechat_Matrix 项目路径
WECHAT_MATRIX_DIR = ""

# 上传队列目录
UPLOAD_QUEUE_DIR = ""
