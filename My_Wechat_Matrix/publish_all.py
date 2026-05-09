from auto_matrix import MatrixAutoScheduler
from pathlib import Path
import time

def main():
    scheduler = MatrixAutoScheduler()
    accounts = scheduler.get_enabled_accounts()
    print(f"找到 {len(accounts)} 个启用账号")
    
    success_count = 0
    for account_dir in accounts:
        if scheduler.has_pending_content(account_dir):
            print(f"\n🚀 正在发布: {account_dir.name}")
            try:
                if scheduler.publish_existing_content(account_dir):
                    success_count += 1
                else:
                    print(f"❌ {account_dir.name} 发布失败")
            except Exception as e:
                print(f"❌ {account_dir.name} 运行出错: {e}")
            
            # 账号间隔
            print("等待 30 秒进入下一个账号...")
            time.sleep(30)
        else:
            print(f"⏭️ {account_dir.name} 没有待发布内容 (output.txt 不存在)")
            
    print(f"\n✅ 发布任务结束，成功: {success_count}/{len(accounts)}")

if __name__ == "__main__":
    main()
