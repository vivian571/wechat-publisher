import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

from generator import ContentGenerator

def verify():
    print("🔍 正在验证 Agency-Agents 集成逻辑...")
    # 初始化生成器 (强制使用本地配置)
    generator = ContentGenerator()
    
    # 模拟为 '零更_PromptBook' 账号加载配置
    account_path = generator.accounts_dir / "零更_PromptBook"
    account_data = generator.load_account_config(account_path)
    
    print("\n✅ 加载成功！")
    print("-" * 50)
    print(f"账号名称: {account_data['config'].get('account_name')}")
    print(f"链接的代理角色: {account_data['config'].get('agency_agent')}")
    
    print("\n--- [解析出的专家原则摘要] ---")
    if account_data['agency_context']:
        print(account_data['agency_context'][:500] + "...")
    else:
        print("❌ 未能解析出专家原则，请检查路径或 Markdown 标题格式。")
    print("-" * 50)

if __name__ == "__main__":
    verify()
