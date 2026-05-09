
import os
import requests
import yaml
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)

def check_token():
    # Load .env from wechat/
    env_path = os.path.join('wechat', '.env')
    print(f"Loading .env from {env_path}")
    load_dotenv(env_path)
    
    account_name = "开源智核"
    app_id = os.getenv(f'WECHAT_ACCOUNT_{account_name}_APP_ID')
    app_secret = os.getenv(f'WECHAT_ACCOUNT_{account_name}_APP_SECRET')
    
    print(f"Account: {account_name}")
    print(f"AppID: {app_id}")
    
    if not app_id or not app_secret:
        print("Error: AppID or AppSecret not found in environment.")
        return

    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if "access_token" in data:
            print("Success! access_token obtained.")
        else:
            print(f"Failed: {data}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_token()
