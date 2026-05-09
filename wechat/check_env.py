import os
import sys
from dotenv import load_dotenv

# 设置控制台输出编码为UTF-8
if sys.platform.startswith('win'):
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== 环境变量检查工具 ===")

# 加载 .env 文件
load_dotenv()

# 检查关键环境变量
env_vars = [
    'WECHAT_APP_ID',
    'WECHAT_APP_SECRET'
]

print("\n当前环境变量:")
print("-" * 50)
for var in env_vars:
    value = os.getenv(var)
    if value is None:
        print(f"{var}: [错误] 未设置")
    else:
        masked_value = f"{value[:3]}...{value[-3:] if len(value) > 6 else ''}"
        print(f"{var}: [已设置] (值: {masked_value} 长度: {len(value)})")

print("\n检查完成。如果看到[错误]，请确保 .env 文件存在且格式正确。")
print("请检查 .env 文件内容是否如下（不要包含引号）：")
print("WECHAT_APP_ID=你的AppID")
print("WECHAT_APP_SECRET=你的AppSecret")
