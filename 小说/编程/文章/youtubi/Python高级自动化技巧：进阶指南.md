# Python高级自动化技巧：进阶指南

嘿，小伙伴们！上次我们一起探索了Python自动化的基础知识，今天我们将深入挖掘更多高级自动化技巧，帮助你将自动化能力提升到一个全新的水平！正如我们在上期互动环节中提到的，今天我们将重点关注GUI自动化、网络爬虫进阶、API集成和机器学习自动化等高级主题。

## GUI自动化：控制你的桌面应用

有些应用程序没有提供API接口，但我们仍然可以通过模拟鼠标点击和键盘输入来实现自动化。Python的PyAutoGUI库就是这样一个强大的工具。

### PyAutoGUI基础操作

```python
import pyautogui
import time

# 安全措施：将鼠标快速移动到屏幕左上角可中断自动化
pyautogui.FAILSAFE = True

# 等待2秒，给你时间切换到目标窗口
time.sleep(2)

# 获取屏幕分辨率
screen_width, screen_height = pyautogui.size()
print(f"屏幕分辨率：{screen_width}x{screen_height}")

# 获取鼠标当前位置
current_x, current_y = pyautogui.position()
print(f"鼠标当前位置：({current_x}, {current_y})")

# 移动鼠标到指定位置并点击
pyautogui.moveTo(500, 300, duration=1)  # 平滑移动，duration指定移动时间
pyautogui.click()  # 在当前位置点击

# 输入文本
pyautogui.typewrite("Hello, PyAutoGUI!", interval=0.1)  # interval控制输入速度

# 按下特殊键
pyautogui.press("enter")
```

### 屏幕识别与智能操作

更高级的GUI自动化可以结合图像识别，让脚本能够"看见"屏幕内容，实现更智能的操作。

```python
import pyautogui

# 查找屏幕上的图像位置
button_location = pyautogui.locateOnScreen("submit_button.png", confidence=0.8)

if button_location:
    # 点击找到的按钮中心
    button_center = pyautogui.center(button_location)
    pyautogui.click(button_center)
    print("成功点击按钮！")
else:
    print("未找到按钮")

# 高级：等待图像出现并点击
def click_when_appears(image_path, timeout=30, confidence=0.8):
    start_time = time.time()
    while time.time() - start_time < timeout:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(pyautogui.center(location))
            return True
        time.sleep(0.5)
    return False

# 使用函数等待并点击登录按钮
success = click_when_appears("login_button.png", timeout=10)
print("登录成功！" if success else "登录超时！")
```

### 实战案例：自动化表单填写

```python
import pyautogui
import pandas as pd
import time

# 读取Excel中的表单数据
df = pd.read_excel("form_data.xlsx")

# 打开浏览器并导航到表单页面（假设已经打开）
time.sleep(3)  # 给你时间手动打开表单页面

# 遍历每一行数据，自动填写表单
for index, row in df.iterrows():
    # 点击姓名输入框并输入
    pyautogui.click(x=300, y=200)
    pyautogui.hotkey("ctrl", "a")  # 全选当前内容
    pyautogui.typewrite(row["姓名"])
    
    # 点击邮箱输入框并输入
    pyautogui.click(x=300, y=250)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(row["邮箱"])
    
    # 点击提交按钮
    pyautogui.click(x=300, y=350)
    
    # 等待提交完成，寻找"提交成功"的提示
    success = click_when_appears("success_message.png", timeout=5)
    
    if success:
        print(f"第{index+1}条数据提交成功")
    else:
        print(f"第{index+1}条数据提交失败")
    
    # 点击"新建表单"按钮继续下一条
    pyautogui.click(x=300, y=400)
    time.sleep(1)  # 等待新表单加载

print("所有数据已成功提交！")
```

## 网络爬虫进阶：突破限制与高效采集

### 反反爬虫策略

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
import random
import time

# 创建会话对象
session = requests.Session()

# 重试策略
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 随机User-Agent
ua = UserAgent()

# 代理IP池（示例）
proxy_pool = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080"
]

# 发送请求
def make_request(url):
    # 随机延时
    time.sleep(random.uniform(1, 3))
    
    # 随机选择代理
    proxy = {"http": random.choice(proxy_pool)}
    
    # 构建请求头
    headers = {
        "User-Agent": ua.random,
        "Referer": "https://www.example.com",  # 伪造来源
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        response = session.get(url, headers=headers, proxies=proxy, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"请求失败: {e}")
        return None

# 使用示例
html = make_request("https://www.example.com")
```

### Selenium与无头浏览器

对于复杂的JavaScript渲染网站，Selenium是一个强大的工具：

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(f"user-agent={UserAgent().random}")

# 初始化浏览器
driver = webdriver.Chrome(options=chrome_options)

try:
    # 访问网页
    driver.get("https://www.example.com")
    
    # 等待特定元素加载完成
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "some-id"))
    )
    
    # 执行JavaScript
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # 等待内容加载
    
    # 获取动态加载的内容
    elements = driver.find_elements(By.CSS_SELECTOR, ".item")
    for element in elements:
        print(element.text)
    
    # 截图
    driver.save_screenshot("screenshot.png")
    
finally:
    driver.quit()
```

### 实战案例：智能数据提取与存储

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import sqlite3

# 创建数据库连接
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    rating REAL,
    url TEXT
)
''')
conn.commit()

# 解析产品页面
def parse_product(url):
    try:
        response = make_request(url)  # 使用前面定义的函数
        if not response:
            return None
            
        soup = BeautifulSoup(response, 'html.parser')
        
        # 提取数据（根据实际网站调整选择器）
        name = soup.select_one('.product-name').text.strip()
        price = float(soup.select_one('.product-price').text.strip().replace('¥', ''))
        rating = float(soup.select_one('.rating-score').text.strip())
        
        return {
            'name': name,
            'price': price,
            'rating': rating,
            'url': url
        }
    except Exception as e:
        print(f"解析产品失败: {url}, 错误: {e}")
        return None

# 获取产品链接列表（示例）
def get_product_urls(base_url, pages=5):
    urls = []
    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        response = make_request(url)
        if not response:
            continue
            
        soup = BeautifulSoup(response, 'html.parser')
        product_links = soup.select('.product-item a')
        
        for link in product_links:
            urls.append(link['href'])
    
    return urls

# 主函数
def main():
    base_url = "https://www.example.com/products"
    product_urls = get_product_urls(base_url)
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(parse_product, product_urls))
    
    # 过滤None结果
    products = [p for p in results if p]
    
    # 保存到数据库
    for product in products:
        cursor.execute(
            "INSERT INTO products (name, price, rating, url) VALUES (?, ?, ?, ?)",
            (product['name'], product['price'], product['rating'], product['url'])
        )
    
    conn.commit()
    print(f"成功抓取并保存了 {len(products)} 个产品信息")
    
    # 导出为Excel
    df = pd.DataFrame(products)
    df.to_excel("products.xlsx", index=False)
    print("数据已导出为Excel文件")

if __name__ == "__main__":
    main()
    conn.close()
```

## API集成：打造强大的数据流

### RESTful API交互

```python
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量中的API密钥
load_dotenv()
api_key = os.getenv("API_KEY")

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.status_code

# 使用示例：天气API
weather_client = APIClient("https://api.weatherapi.com/v1", api_key)

def get_weather(city):
    try:
        data = weather_client.get("current.json", params={"q": city})
        return {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"]
        }
    except Exception as e:
        print(f"获取天气信息失败: {e}")
        return None

# 获取北京天气
beijing_weather = get_weather("Beijing")
print(json.dumps(beijing_weather, indent=4, ensure_ascii=False))
```

### 多API集成与数据流

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# 加载环境变量
load_dotenv()
stock_api_key = os.getenv("STOCK_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

# 股票API客户端
stock_client = APIClient("https://api.stockdata.com/v1", stock_api_key)

# 新闻API客户端
news_client = APIClient("https://api.newsapi.org/v2", news_api_key)

# 获取股票历史数据
def get_stock_history(symbol, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    params = {
        "symbol": symbol,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    data = stock_client.get("historical", params=params)
    return pd.DataFrame(data["data"])

# 获取相关新闻
def get_related_news(company_name, days=7):
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    params = {
        "q": company_name,
        "from": from_date,
        "sortBy": "popularity",
        "language": "zh"
    }
    
    data = news_client.get("everything", params=params)
    return data["articles"]

# 分析股票与新闻的关联
def analyze_stock_and_news(symbol, company_name):
    # 获取股票数据
    stock_df = get_stock_history(symbol)
    
    # 获取新闻数据
    news = get_related_news(company_name)
    
    # 绘制股票走势图
    plt.figure(figsize=(12, 6))
    plt.plot(stock_df["date"], stock_df["close"])
    plt.title(f"{company_name}({symbol}) 股价走势")
    plt.xlabel("日期")
    plt.ylabel("收盘价")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{symbol}_stock_trend.png")
    
    # 整合新闻与股价数据
    news_dates = [datetime.strptime(article["publishedAt"][:10], "%Y-%m-%d") for article in news]
    news_df = pd.DataFrame({
        "date": news_dates,
        "title": [article["title"] for article in news],
        "url": [article["url"] for article in news]
    })
    
    # 合并数据
    merged_data = pd.merge(
        stock_df, 
        news_df, 
        left_on="date", 
        right_on="date", 
        how="left"
    )
    
    # 输出分析报告
    merged_data.to_excel(f"{symbol}_analysis.xlsx", index=False)
    print(f"分析报告已保存为 {symbol}_analysis.xlsx")

# 使用示例
analyze_stock_and_news("AAPL", "Apple")
```

### 实战案例：自动化社交媒体管理

```python
import tweepy
import schedule
import time
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Twitter API凭证
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# 认证并创建API对象
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# 从Excel读取预定的推文
def load_scheduled_tweets():
    df = pd.read_excel("scheduled_tweets.xlsx")
    return df.to_dict("records")

# 发送推文
def send_tweet(content, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            # 带图片的推文
            media = api.media_upload(image_path)
            api.update_status(content, media_ids=[media.media_id])
        else:
            # 纯文本推文
            api.update_status(content)
        print(f"推文发送成功: {content[:30]}...")
        return True
    except Exception as e:
        print(f"发送推文失败: {e}")
        return False

# 监控关键词并回复
def monitor_and_reply():
    # 获取提及我们的最新推文
    mentions = api.mentions_timeline(count=10)
    
    for mention in mentions:
        # 检查是否已回复过（可以用数据库记录）
        if is_already_replied(mention.id):
            continue
        
        # 根据内容生成回复
        reply_text = generate_reply(mention.text)
        
        # 回复推文
        api.update_status(
            f"@{mention.user.screen_name} {reply_text}",
            in_reply_to_status_id=mention.id
        )
        
        # 记录已回复
        mark_as_replied(mention.id)

# 检查是否已回复（示例实现）
def is_already_replied(tweet_id):
    # 这里应该查询数据库
    # 简化示例，实际应使用数据库
    replied_ids_file = "replied_tweets.txt"
    
    if not os.path.exists(replied_ids_file):
        return False
        
    with open(replied_ids_file, "r") as f:
        replied_ids = f.read().splitlines()
    
    return str(tweet_id) in replied_ids

# 标记为已回复
def mark_as_replied(tweet_id):
    with open("replied_tweets.txt", "a") as f:
        f.write(f"{tweet_id}\n")

# 生成回复内容（可以使用更智能的方法）
def generate_reply(tweet_text):
    # 简单示例，实际可以使用NLP或规则引擎
    if "问题" in tweet_text or "帮助" in tweet_text:
        return "感谢您的提问！请发送邮件至support@example.com，我们的团队会尽快回复您。"
    elif "赞" in tweet_text or "喜欢" in tweet_text:
        return "非常感谢您的支持！我们会继续努力提供更好的内容和服务。"
    else:
        return "谢谢您的关注！如有任何问题，请随时告诉我们。"

# 定时任务：发送预定推文
def post_scheduled_tweets():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    
    tweets = load_scheduled_tweets()
    
    for tweet in tweets:
        # 检查是否应该发送
        if tweet["date"] == current_date and tweet["time"] == current_time:
            send_tweet(tweet["content"], tweet.get("image_path"))

# 设置定时任务
schedule.every(1).minutes.do(post_scheduled_tweets)
schedule.every(15).minutes.do(monitor_and_reply)

# 运行定时任务
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
```

## 机器学习自动化：智能决策与预测

### 自动化模型训练与评估

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# 自动化模型训练流程
class AutoML:
    def __init__(self, data_path, target_column, test_size=0.2, random_state=42):
        self.data_path = data_path
        self.target_column = target_column
        self.test_size = test_size
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        
    def load_data(self):
        # 根据文件类型加载数据
        if self.data_path.endswith('.csv'):
            self.df = pd.read_csv(self.data_path)
        elif self.data_path.endswith('.xlsx'):
            self.df = pd.read_excel(self.data_path)
        else:
            raise ValueError("不支持的文件格式，请提供CSV或Excel文件")
        
        print(f"数据加载完成，共 {self.df.shape[0]} 行，{self.df.shape[1]} 列")
        return self
    
    def preprocess(self):
        # 分离特征和目标变量
        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]
        
        # 处理分类特征
        cat_columns = X.select_dtypes(include=['object', 'category']).columns
        X = pd.get_dummies(X, columns=cat_columns, drop_first=True)
        
        # 分割训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        # 标准化数值特征
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        
        print("数据预处理完成")
        return self
    
    def train(self, param_grid=None):
        if param_grid is None:
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        
        # 使用网格搜索找到最佳参数
        rf = RandomForestClassifier(random_state=self.random_state)
        grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(self.X_train, self.y_train)
        
        # 获取最佳模型
        self.model = grid_search.best_estimator_
        print(f"模型训练完成，最佳参数: {grid_search.best_params_}")
        return self
    
    def evaluate(self):
        # 在测试集上评估模型
        y_pred = self.model.predict(self.X_test)
        
        # 打印分类报告
        print("\n分类报告:")
        print(classification_report(self.y_test, y_pred))
        
        # 绘制混淆矩阵
        cm = confusion_matrix(self.y_test, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('预测标签')
        plt.ylabel('真实标签')
        plt.title('混淆矩阵')
        plt.savefig('confusion_matrix.png')
        
        # 特征重要性
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.df.drop(columns=[self.target_column]).columns
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            plt.figure(figsize=(12, 8))
            plt.title('特征重要性')
            plt.bar(range(len(importances)), importances[indices])
            plt.xticks(range(len(importances)), feature_names[indices], rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('feature_importance.png')
            
        return self
    
    def save_model(self, model_path='model.pkl', scaler_path='scaler.pkl'):
        # 保存模型和数据预处理器
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f"模型已保存至 {model_path}")
        print(f"数据预处理器已保存至 {scaler_path}")
        
        # 保存模型元数据
        metadata = {
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': type(self.model).__name__,
            'feature_count': self.X_train.shape[1],
            'target_column': self.target_column,
            'accuracy': self.model.score(self.X_test, self.y_test)
        }
        
        # 将元数据保存为JSON文件
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"模型元数据已保存至 {metadata_path}")
        
        return self
