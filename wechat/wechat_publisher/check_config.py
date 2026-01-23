import os
import sys
from dotenv import load_dotenv

# 设置控制台编码为UTF-8
if sys.platform.startswith('win'):
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def print_status(icon, message):
    print(f"{icon} {message}")

print("=== 配置检查工具 ===")

# 尝试加载 .env 文件
env_loaded = load_dotenv()
if not env_loaded:
    print("警告: 未找到 .env 文件")

# 检查关键环境变量
required_vars = {
    'WECHAT_APP_ID': '微信应用ID',
    'WECHAT_APP_SECRET': '微信应用密钥',
    'WATCH_DIR': '监控的文档目录',
    'IMAGE_DIR': '图片目录'
}

print("\n当前环境变量配置:")
all_set = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if not value:
        print_status("[!]", f"{var} ({desc}): 未设置")
        all_set = False
    else:
        print_status("[√]", f"{var}: 已设置")

if all_set:
    print("\n[√] 所有必需的环境变量都已正确设置！")
else:
    print("\n[!] 请确保所有必需的环境变量都已正确设置。")
    
    # 创建.env文件的内容
    env_content = """# 微信公众平台配置
WECHAT_APP_ID=你的AppID
WECHAT_APP_SECRET=你的AppSecret

# 路径配置
WATCH_DIR=./documents  # 监控的文档目录
IMAGE_DIR=./images     # 图片目录
"""
    
    # 尝试创建.env文件
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if not os.path.exists(env_path):
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print(f"\n[!] 已创建 .env 文件，请编辑以下文件并填写正确的配置：")
            print(f"    文件路径: {env_path}")
        else:
            print("\n[!] 请编辑 .env 文件并填写以下配置：")
        
        print("\n" + "-"*50)
        print(env_content)
        print("-"*50)
        
    except Exception as e:
        print(f"\n[!] 无法自动创建 .env 文件: {str(e)}")
        print("\n请手动创建 .env 文件并添加以下内容：")
        print("\n" + "-"*50)
        print(env_content)
        print("-"*50)
