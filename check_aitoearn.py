import os
import requests
import json
from dotenv import load_dotenv

# Load env from openclaw directory
load_dotenv('/Volumes/Crucial X9/openclaw/.env')

api_key = os.getenv('AITOEARN_API_KEY')
if not api_key:
    print("API Key not found in .env")
    exit(1)

url = "https://aitoearn.ai/api/unified/mcp"
headers = {
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}

response = requests.post(url, headers=headers, json=payload)
print(response.status_code)
try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(response.text)
