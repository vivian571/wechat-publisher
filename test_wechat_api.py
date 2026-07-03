import requests
import json
import os

def test_wechat_api():
    # 从 matrix_config.json 读取配置
    config_path = "/Users/ax/公众号写作/My_Wechat_Matrix/matrix_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    app_id = config['wechat_config']['app_id']
    app_secret = config['wechat_config']['app_secret']
    
    print(f"Testing connectivity for AppID: {app_id}")
    
    # 微信稳定版获取 Token 接口
    url = f"https://api.weixin.qq.com/cgi-bin/stable_token"
    data = {
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if "access_token" in result:
            print("✅ Access Token 获取成功！IP 白名单已生效。")
            return True
        else:
            print(f"❌ 获取失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 请求发生异常: {e}")
        return False

if __name__ == "__main__":
    test_wechat_api()
