import os
import sys
from wechat_publisher import WeChatPublisher

def main():
    # 从环境变量获取配置
    app_id = os.getenv('WECHAT_ACCOUNT_码趣逻辑站_APP_ID')
    app_secret = os.getenv('WECHAT_ACCOUNT_码趣逻辑站_APP_SECRET')
    
    if not app_id or not app_secret:
        print("错误：未找到微信公众号的 AppID 或 AppSecret")
        print("请确保 .env 文件中包含 WECHAT_ACCOUNT_码趣逻辑站_APP_ID 和 WECHAT_ACCOUNT_码趣逻辑站_APP_SECRET")
        return
    
    # 初始化发布器
    publisher = WeChatPublisher("码趣逻辑站", app_id, app_secret, "码趣逻辑站")
    
    # 测试发布
    test_file = os.path.join('documents', '码趣逻辑站', 'test_publish.md')
    print(f"正在发布文件: {test_file}")
    
    try:
        result = publisher.process_document(test_file)
        if result:
            print("发布成功！")
        else:
            print("发布失败，请查看日志获取详细信息。")
    except Exception as e:
        print(f"发布过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
