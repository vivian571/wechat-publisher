# Python高级架构：构建企业级应用的技术体系

## 引言

在Python系统VIP A1课程的第四部分，我们将深入学习Python高级架构。随着你的Python技能不断提升，如何设计和构建可扩展、可维护的企业级应用成为关键挑战。本文将详细介绍Python高级架构模块的学习内容，帮助你掌握从微信小程序到人工智能的高级应用开发技能。

## 微信小程序

微信小程序是一种不需要下载安装即可使用的应用，它实现了「触手可及」的梦想。Python开发者可以通过后端API为小程序提供数据支持。

### 小程序架构

```python
# 小程序后端API示例（使用Flask框架）
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # 处理跨域请求

@app.route('/api/products', methods=['GET'])
def get_products():
    # 模拟数据库查询
    products = [
        {"id": 1, "name": "Python入门课程", "price": 199},
        {"id": 2, "name": "Django实战", "price": 299},
        {"id": 3, "name": "数据分析精讲", "price": 399}
    ]
    return jsonify({"code": 0, "data": products})

@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 实际应用中应查询数据库验证用户
    if username == 'test' and password == '123456':
        return jsonify({"code": 0, "msg": "登录成功", "token": "sample_token"})
    else:
        return jsonify({"code": 1, "msg": "用户名或密码错误"})

if __name__ == '__main__':
    app.run(debug=True)
```

### 页面开发

小程序前端开发主要使用WXML、WXSS和JavaScript：

```javascript
// 小程序页面逻辑示例 (index.js)
Page({
  data: {
    products: [],
    loading: true
  },
  onLoad: function() {
    this.fetchProducts()
  },
  fetchProducts: function() {
    wx.request({
      url: 'http://localhost:5000/api/products',
      method: 'GET',
      success: (res) => {
        if(res.data.code === 0) {
          this.setData({
            products: res.data.data,
            loading: false
          })
        }
      },
      fail: (err) => {
        console.error('请求失败', err)
        this.setData({loading: false})
      }
    })
  }
})
```

### API调用

小程序与Python后端的数据交互：

```python
# 使用requests库模拟小程序API调用
import requests

def test_api():
    # 测试登录API
    login_url = "http://localhost:5000/api/user/login"
    login_data = {"username": "test", "password": "123456"}
    response = requests.post(login_url, json=login_data)
    print("登录结果:", response.json())
    
    # 获取token
    token = response.json().get("token")
    
    # 测试获取产品列表API
    products_url = "http://localhost:5000/api/products"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(products_url, headers=headers)
    print("产品列表:", response.json())

if __name__ == "__main__":
    test_api()
```

## Flask框架

Flask是一个轻量级的Python Web框架，它灵活、简单且易于扩展。

### Flask基础

```python
# Flask基础应用
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'some_secret_key'

@app.route('/')
def index():
    return render_template('index.html', title='Flask Demo')

@app.route('/about')
def about():
    return render_template('about.html', title='关于我们')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # 处理表单数据，例如发送邮件或保存到数据库
        # ...
        
        flash('消息已发送，我们会尽快回复您！', 'success')
        return redirect(url_for('index'))
    
    return render_template('contact.html', title='联系我们')

if __name__ == '__main__':
    app.run(debug=True)
```

### 蓝图

蓝图用于组织相关视图和其他代码：

```python
# 使用蓝图组织应用结构
from flask import Flask, render_template
from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_bp = Blueprint('user', __name__, url_prefix='/user')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 蓝图路由
@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html')

@user_bp.route('/profile')
def profile():
    return render_template('user/profile.html')

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

# 创建应用并注册蓝图
app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### 扩展

Flask扩展丰富了框架功能：

```python
# Flask常用扩展示例
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # 数据库ORM
from flask_migrate import Migrate  # 数据库迁移
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  # 用户认证
from flask_wtf import FlaskForm  # 表单处理
from wtforms import StringField, PasswordField, SubmitField  # 表单字段
from wtforms.validators import DataRequired, Email, Length  # 表单验证

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(128))

# 登录表单
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('登录')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # 实际应用中应使用密码哈希
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

## 爬虫技术

爬虫是自动获取网页内容的程序，Python拥有强大的爬虫生态系统。

### 请求库

```python
# 使用requests库发送HTTP请求
import requests
from bs4 import BeautifulSoup
import time

def basic_scraper(url):
    # 设置请求头，模拟浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果请求不成功则抛出异常
        
        # 设置编码
        response.encoding = response.apparent_encoding
        
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    url = "https://www.example.com"
    html = basic_scraper(url)
    
    if html:
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.title.text
        print(f"页面标题: {title}")
        
        # 提取所有链接
        links = soup.find_all('a')
        print(f"找到 {len(links)} 个链接")
        
        for link in links[:5]:  # 只打印前5个链接
            print(link.get('href'))
```

### 解析库

```python
# 使用不同的解析库提取数据
import requests
from bs4 import BeautifulSoup
import lxml.html
import re
import json

def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text

# BeautifulSoup解析
def parse_with_bs4(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取数据示例
    title = soup.title.text
    headings = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [p.text for p in soup.find_all('p')]
    
    # CSS选择器
    main_content = soup.select('div.main-content')
    nav_items = soup.select('nav ul li a')
    
    return {
        'title': title,
        'headings': headings[:3],  # 前3个标题
        'paragraphs': paragraphs[:3],  # 前3个段落
        'nav_items_count': len(nav_items)
    }

# lxml解析
def parse_with_lxml(html):
    tree = lxml.html.fromstring(html)
    
    # XPath选择器
    title = tree.xpath('//title/text()')[0]
    headings = tree.xpath('//h1/text() | //h2/text() | //h3/text()')
    paragraphs = tree.xpath('//p/text()')
    
    return {
        'title': title,
        'headings': headings[:3],
        'paragraphs': paragraphs[:3]
    }

# 正则表达式解析
def parse_with_regex(html):
    title_match = re.search('<title>(.*?)</title>', html, re.DOTALL)
    title = title_match.group(1) if title_match else 'No title found'
    
    # 提取所有链接
    links = re.findall('href=[\'"]([^\'"]+)[\'"]', html)
    
    return {
        'title': title,
        'links_count': len(links),
        'links': links[:5]  # 前5个链接
    }

# 使用示例
if __name__ == "__main__":
    url = "https://www.example.com"
    html = fetch_page(url)
    
    print("\nBeautifulSoup解析结果:")
    print(json.dumps(parse_with_bs4(html), indent=2, ensure_ascii=False))
    
    print("\nlxml解析结果:")
    print(json.dumps(parse_with_lxml(html), indent=2, ensure_ascii=False))
    
    print("\n正则表达式解析结果:")
    print(json.dumps(parse_with_regex(html), indent=2, ensure_ascii=False))
```

### Scrapy框架

Scrapy是一个强大的爬虫框架，适合大规模爬虫项目：

```python
# Scrapy爬虫示例

# 项目结构
# my_scraper/
#   scrapy.cfg
#   my_scraper/
#     __init__.py
#     items.py
#     middlewares.py
#     pipelines.py
#     settings.py
#     spiders/
#       __init__.py
#       news_spider.py

# items.py - 定义数据结构
from scrapy import Item, Field

class NewsItem(Item):
    title = Field()
    url = Field()
    content = Field()
    author = Field()
    publish_date = Field()
    category = Field()

# news_spider.py - 爬虫实现
import scrapy
from ..items import NewsItem

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['example.com']
    start_urls = ['https://example.com/news/']
    
    def parse(self, response):
        # 提取新闻列表页中的新闻链接
        news_links = response.css('div.news-list a::attr(href)').getall()
        
        for link in news_links:
            # 构建完整URL并发送请求
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_news)
        
        # 处理分页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
    
    def parse_news(self, response):
        # 提取新闻详情
        item = NewsItem()
        item['title'] = response.css('h1.title::text').get()
        item['url'] = response.url
        item['content'] = ''.join(response.css('div.content p::text').getall())
        item['author'] = response.css('span.author::text').get()
        item['publish_date'] = response.css('span.date::text').get()
        item['category'] = response.css('span.category::text').get()
        
        yield item

# pipelines.py - 数据处理
import json
from itemadapter import ItemAdapter

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('news_data.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True
    
    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        line = json.dumps(adapter.asdict(), ensure_ascii=False)
        
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(',\n')
        
        self.file.write('  ' + line)
        return item

# settings.py - 配置文件
BOT_NAME = 'my_scraper'

SPIDER_MODULES = ['my_scraper.spiders']
NEWSPIDER_MODULE = 'my_scraper.spiders'

# 请求头设置
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'

# 遵守robots.txt规则
ROBOTSTXT_OBEY = True

# 并发请求数
CONCURRENT_REQUESTS = 16

# 下载延迟
DOWNLOAD_DELAY = 3

# 启用中间件
DOWNLOADER_MIDDLEWARES = {
   'my_scraper.middlewares.MyScraperDownloaderMiddleware': 543,
}

# 启用管道
ITEM_PIPELINES = {
   'my_scraper.pipelines.JsonWriterPipeline': 300,
}
```

## 数据分析

Python是数据分析的首选语言，拥有强大的数据处理库。

### NumPy

NumPy是Python科学计算的基础库：

```python
# NumPy基础操作
import numpy as np

# 创建数组
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.zeros((3, 4))  # 3x4的零矩阵
arr3 = np.ones((2, 3, 4))  # 2x3x4的1矩阵
arr4 = np.arange(10, 30, 5)  # [10, 15, 20, 25]
arr5 = np.linspace(0, 1, 5)  # 均匀分布的5个点

print("数组形状:", arr1.shape)
print("数组维度:", arr1.ndim)
print("数组元素类型:", arr1.dtype)

# 数组操作
arr = np.array([[1, 2, 3], [4, 5, 6]])
print("转置:", arr.T)
print("求和:", arr.sum())
print("按行求和:", arr.sum(axis=1))
print("按列求和:", arr.sum(axis=0))
print("最大值:", arr.max())
print("最小值:", arr.min())
print("平均值:", arr.mean())

# 数组索引和切片
arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print("第二行:", arr[1])
print("第三列:", arr[:, 2])
print("子矩阵:", arr[1:3, 0:2])

# 数组运算
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("加法:", a + b)  # 或 np.add(a, b)
print("减法:", a - b)  # 或 np.subtract(a, b)
print("乘法:", a * b)  # 或 np.multiply(a, b)
print("除法:", a / b)  # 或 np.divide(a, b)
print("点积:", np.dot(a, b))

# 数组变形
arr = np.arange(12)
print("原数组:", arr)
print("重塑为3x4矩阵:\n", arr.reshape(3, 4))
print("展平:", arr.reshape(3, 4).flatten())
```

### Pandas

Pandas提供了高效的数据结构和数据分析工具：

```python
# Pandas基础操作
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建Series
s = pd.Series([1, 3, 5, np.nan, 6, 8])
print("Series:\n", s)

# 创建DataFrame
dates = pd.date_range('20230101', periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))
print("\nDataFrame:\n", df)

# 从字典创建DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40],
    'city': ['New York', 'Paris', 'London', 'Tokyo'],
    'salary': [50000, 60000, 70000, 80000]
}
df2 = pd.DataFrame(data)
print("\n从字典创建DataFrame:\n", df2)

# 查看数据
print("\n前3行:\n", df.head(3))
print("\n后2行:\n", df.tail(2))
print("\n索引:\n", df.index)
print("\n列名:\n", df.columns)
print("\n数据统计:\n", df.describe())
print("\n转置:\n", df.T)

# 数据选择
print("\n选择列A:\n", df['A'])
print("\n选择前3行:\n", df[:3])
print("\n按标签选择:\n", df.loc[dates[0]])
print("\n多轴标签选择:\n", df.loc[:, ['A', 'B']])
print("\n按位置选择:\n", df.iloc[3:5, 0:2])

# 数据过滤
print("\nA>0的行:\n", df[df.A > 0])

# 缺失值处理
df3 = df.copy()
df3.iloc[0, 1] = np.nan
df3.iloc[1, 2] = np.nan
print("\n包含NaN的DataFrame:\n", df3)
print("\n删除包含NaN的行:\n", df3.dropna())
print("\n填充NaN:\n", df3.fillna(value=0))

# 数据操作
print("\n按列求和:\n", df.sum())
print("\n按行求和:\n", df.sum(axis=1))
print("\n排序:\n", df.sort_values(by='B'))

# 数据合并
left = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                     'A': ['A0', 'A1', 'A2', 'A3'],
                     'B': ['B0', 'B1', 'B2', 'B3']})

right = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                      'C': ['C0', 'C1', 'C2', 'C3'],
                      'D': ['D0', 'D1', 'D2', 'D3']})

print("\n合并DataFrame:\n", pd.merge(left, right, on='key'))

# 数据分组
df4 = pd.DataFrame({
    'A': ['foo', 'bar', 'foo', 'bar', 'foo', 'bar'],
    'B': ['one', 'one', 'two', 'three', 'two', 'two'],
    'C': np.random.randn(6),
    'D': np.random.randn(6)
})

print("\n分组求和:\n", df4.groupby('A').sum())
print("\n多列分组:\n", df4.groupby(['A', 'B']).sum())

# 数据透视表
print("\n数据透视表:\n", pd.pivot_table(df4, values='D', index=['A', 'B'], columns=['C']))

# 时间序列
rng = pd.date_range('1/1/2023', periods=100, freq='D')
ts = pd.Series(np.random.randn(len(rng)), index=rng)
print("\n时间序列:\n", ts.head())
print("\n按月重采样:\n", ts.resample('M').mean())

# 数据可视化
ts_cumsum = ts.cumsum()
ts_cumsum.plot()
plt.title('累积和时间序列')
plt.savefig('pandas_plot.png')  # 保存图表
plt.close()  # 关闭图表

# 数据导入导出
# CSV
df.to_csv('data.csv')
df_csv = pd.read_csv('data.csv', index_col=0)

# Excel
df.to_excel('data.xlsx', sheet_name='Sheet1')
df_excel = pd.read_excel('data.xlsx', 'Sheet1', index_col=0)

# SQL
# 需要安装sqlalchemy
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///data.db')
# df.to_sql('data_table', engine)
# df_sql = pd.read_sql('select * from data_table', engine)
```

### 数据处理

```python
# 数据清洗与预处理
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer

# 创建示例数据
data = {
    'age': [25, 30, np.nan, 40, 35],
    'income': [50000, np.nan, 70000, 80000, 65000],
    'gender': ['M', 'F', 'M', 'F', np.nan],
    'education': ['Bachelor', 'Master', np.nan, 'PhD', 'Bachelor'],
    'satisfaction': [3, 4, 5, np.nan, 4]
}

df = pd.DataFrame(data)
print("原始数据:\n", df)

# 1. 缺失值处理
# 查看缺失值
print("\n缺失值统计:\n", df.isnull().sum())

# 填充缺失值
# 数值型数据用均值填充
imputer_num = SimpleImputer(strategy='mean')
df[['age', 'income', 'satisfaction']] = imputer_num.fit_transform(df[['age', 'income', 'satisfaction']])

# 分类型数据用众数填充
imputer_cat = SimpleImputer(strategy='most_frequent')
df[['gender', 'education']] = imputer_cat.fit_transform(df[['gender', 'education']])

print("\n填充后的数据:\n", df)

# 2. 特征缩放
# 标准化 (均值为0，标准差为1)
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[['age', 'income']] = scaler.fit_transform(df[['age', 'income']])
print("\n标准化后的数据:\n", df_scaled[['age', 'income']])

# 归一化 (缩放到0-1之间)
min_max_scaler = MinMaxScaler()
df_normalized = df.copy()
df_normalized[['age', 'income']] = min_max_scaler.fit_transform(df[['age', 'income']])
print("\n归一化后的数据:\n", df_normalized[['age', 'income']])

# 3. 编码分类变量
# 标签编码
label_encoder = LabelEncoder()
df_encoded = df.copy()
df_encoded['gender_encoded'] = label_encoder.fit_transform(df['gender'])
df_encoded['education_encoded'] = label_encoder.fit_transform(df['education'])
print("\n标签编码后的数据:\n", df_encoded)

# 独热编码
df_dummies = pd.get_dummies(df, columns=['gender', 'education'], prefix=['gender', 'edu'])
print("\n独热编码后的数据:\n", df_dummies.head())
```

## 可视化技术

数据可视化是数据分析的重要组成部分，Python提供了多种可视化库。

### Matplotlib

Matplotlib是Python最基础的可视化库：

```python
# Matplotlib基础绘图
import matplotlib.pyplot as plt
import numpy as np

# 基础线图
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='sin(x)', color='blue', linestyle='-', linewidth=2)
plt.plot(x, y2, label='cos(x)', color='red', linestyle='--', linewidth=2)
plt.title('正弦和余弦函数')
plt.xlabel('x值')
plt.ylabel('y值')
plt.legend()
plt.grid(True)
plt.savefig('trig_functions.png', dpi=300)
plt.close()

# 子图
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)  # 2行2列的第1个子图
plt.plot(x, y1, 'b-')
plt.title('正弦函数')

plt.subplot(2, 2, 2)  # 2行2列的第2个子图
plt.plot(x, y2, 'r--')
plt.title('余弦函数')

plt.subplot(2, 2, 3)  # 2行2列的第3个子图
plt.plot(x, np.tan(x), 'g-')
plt.title('正切函数')
plt.ylim(-5, 5)  # 限制y轴范围

plt.subplot(2, 2, 4)  # 2行2列的第4个子图
plt.plot(x, x**2, 'm-')
plt.title('平方函数')

plt.tight_layout()  # 调整子图布局
plt.savefig('multiple_plots.png', dpi=300)
plt.close()

# 散点图
n = 50
x = np.random.rand(n)
y = np.random.rand(n)
colors = np.random.rand(n)
sizes = 1000 * np.random.rand(n)

plt.figure(figsize=(10, 6))
plt.scatter(x, y, c=colors, s=sizes, alpha=0.5, cmap='viridis')
plt.colorbar(label='颜色值')
plt.title('散点图示例')
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.savefig('scatter_plot.png', dpi=300)
plt.close()

# 柱状图
categories = ['A', 'B', 'C', 'D', 'E']
values = [25, 40, 30, 55, 15]

plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='skyblue', edgecolor='navy')
plt.title('柱状图示例')
plt.xlabel('类别')
plt.ylabel('数值')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('bar_chart.png', dpi=300)
plt.close()

# 饼图
labels = ['A类', 'B类', 'C类', 'D类', 'E类']
sizes = [15, 30, 25, 10, 20]
explode = (0, 0.1, 0, 0, 0)  # 突出显示第二个扇形

plt.figure(figsize=(10, 6))
plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90, colors=plt.cm.Paired.colors)
plt.axis('equal')  # 保证饼图是圆的
plt.title('饼图示例')
plt.savefig('pie_chart.png', dpi=300)
plt.close()

# 直方图
data = np.random.randn(1000)  # 生成1000个标准正态分布随机数

plt.figure(figsize=(10, 6))
plt.hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('直方图示例')
plt.xlabel('值')
plt.ylabel('频率')
plt.grid(axis='y', alpha=0.75)
plt.savefig('histogram.png', dpi=300)
plt.close()

# 箱线图
data = [np.random.normal(0, std, 100) for std in range(1, 6)]

plt.figure(figsize=(10, 6))
plt.boxplot(data, patch_artist=True, labels=['1', '2', '3', '4', '5'])
plt.title('箱线图示例')
plt.xlabel('组别')
plt.ylabel('值')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('box_plot.png', dpi=300)
plt.close()

# 热图
data = np.random.rand(10, 10)
plt.figure(figsize=(10, 8))
plt.imshow(data, cmap='hot', interpolation='nearest')
plt.colorbar(label='值')
plt.title('热图示例')
plt.savefig('heatmap.png', dpi=300)
plt.close()

# 3D图
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 生成数据
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# 绘制3D表面
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
ax.set_title('3D表面图示例')
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
ax.set_zlabel('Z轴')
plt.savefig('3d_surface.png', dpi=300)
plt.close()
```

### Seaborn

Seaborn是基于Matplotlib的高级可视化库，提供了更美观的默认样式和更高级的绘图功能：

```python
# Seaborn可视化示例
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置样式
sns.set(style="whitegrid")

# 加载示例数据集
tips = sns.load_dataset("tips")
iris = sns.load_dataset("iris")
titanic = sns.load_dataset("titanic")

# 散点图
plt.figure(figsize=(10, 6))
sns.scatterplot(x="total_bill", y="tip", hue="time", size="size", data=tips)
plt.title('小费数据散点图')
plt.savefig('seaborn_scatter.png', dpi=300)
plt.close()

# 回归图
plt.figure(figsize=(10, 6))
sns.regplot(x="total_bill", y="tip", data=tips, scatter_kws={"color": "blue"}, line_kws={"color": "red"})
plt.title('小费与账单总额回归关系')
plt.savefig('seaborn_regplot.png', dpi=300)
plt.close()

# 成对关系图
sns.pairplot(iris, hue="species", height=2.5)
plt.suptitle('鸢尾花数据集特征关系', y=1.02)
plt.savefig('seaborn_pairplot.png', dpi=300)
plt.close()

# 箱线图
plt.figure(figsize=(12, 6))
sns.boxplot(x="day", y="total_bill", hue="smoker", data=tips, palette="Set3")
plt.title('不同日期的账单金额箱线图')
plt.savefig('seaborn_boxplot.png', dpi=300)
plt.close()

# 小提琴图
plt.figure(figsize=(12, 6))
sns.violinplot(x="day", y="total_bill", hue="smoker", data=tips, split=True, palette="Set2")
plt.title('不同日期的账单金额小提琴图')
plt.savefig('seaborn_violinplot.png', dpi=300)
plt.close()

# 热图
corr = iris.drop("species", axis=1).corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title('鸢尾花特征相关性热图')
plt.savefig('seaborn_heatmap.png', dpi=300)
plt.close()

# 分类散点图
plt.figure(figsize=(12, 6))
sns.swarmplot(x="day", y="total_bill", hue="sex", data=tips, palette="Set2")
plt.title('不同日期的账单金额分类散点图')
plt.savefig('seaborn_swarmplot.png', dpi=300)
plt.close()

# 计数图
plt.figure(figsize=(10, 6))
sns.countplot(x="class", hue="survived", data=titanic, palette="Set1")
plt.title('泰坦尼克号不同舱位的生存情况')
plt.savefig('seaborn_countplot.png', dpi=300)
plt.close()

# 分布图
plt.figure(figsize=(10, 6))
sns.histplot(tips["total_bill"], kde=True, color="skyblue")
plt.title('账单金额分布图')
plt.savefig('seaborn_histplot.png', dpi=300)
plt.close()

# 双变量分布图
plt.figure(figsize=(10, 6))
sns.kdeplot(data=tips, x="total_bill", y="tip", cmap="Blues", fill=True)
plt.title('账单金额与小费的双变量分布')
plt.savefig('seaborn_kdeplot.png', dpi=300)
plt.close()

# 分面网格图
g = sns.FacetGrid(tips, col="time", row="sex", height=4)
g.map_dataframe(sns.scatterplot, x="total_bill", y="tip")
g.add_legend()
plt.savefig('seaborn_facetgrid.png', dpi=300)
plt.close()

# 线性模型图
sns.lmplot(x="total_bill", y="tip", hue="smoker", col="time", row="sex", data=tips, height=4)
plt.savefig('seaborn_lmplot.png', dpi=300)
plt.close()
```

## 机器学习基础

Python的scikit-learn库提供了丰富的机器学习算法和工具。

### 监督学习

```python
# 监督学习示例
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris, load_breast_cancer, load_boston, load_diabetes
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

# 分类问题 - 鸢尾花分类
iris = load_iris()
X, y = iris.data, iris.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 创建分类器
classifiers = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'SVM': SVC(random_state=42),
    'KNN': KNeighborsClassifier()
}

# 评估不同分类器
for name, clf in classifiers.items():
    # 训练模型
    clf.fit(X_train, y_train)
    
    # 预测
    y_pred = clf.predict(X_test)
    
    # 评估
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{name} 准确率: {accuracy:.4f}")
    print("分类报告:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

# 回归问题 - 波士顿房价预测
from sklearn.datasets import fetch_california_housing
housing = fetch_california_housing()
X, y = housing.data, housing.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 创建回归器
regressors = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42)
}

# 评估不同回归器
for name, reg in regressors.items():
    # 训练模型
    reg.fit(X_train, y_train)
    
    # 预测
    y_pred = reg.predict(X_test)
    
    # 评估
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"\n{name} MSE: {mse:.4f}, R²: {r2:.4f}")

# 使用管道进行预处理和模型训练
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42))
])

# 使用交叉验证评估模型
cv_scores = cross_val_score(pipeline, X, y, cv=5)
print(f"\n交叉验证准确率: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# 绘制学习曲线
train_sizes, train_scores, test_scores = learning_curve(
    pipeline, X, y, cv=5, n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 10))

train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
test_mean = np.mean(test_scores, axis=1)
test_std = np.std(test_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, color='blue', marker='o', markersize=5, label='训练集准确率')
plt.fill_between(train_sizes, train_mean + train_std, train_mean - train_std, alpha=0.15, color='blue')
plt.plot(train_sizes, test_mean, color='green', marker='s', markersize=5, label='验证集准确率')
plt.fill_between(train_sizes, test_mean + test_std, test_mean - test_std, alpha=0.15, color='green')
plt.title('学习曲线')
plt.xlabel('训练样本数')
plt.ylabel('准确率')
plt.legend(loc='lower right')
plt.grid(True)
plt.savefig('learning_curve.png', dpi=300)
plt.close()
```

### 无监督学习

```python
# 无监督学习示例
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs, make_moons, fetch_olivetti_faces
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, NMF
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# 生成聚类数据
X, y = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=42)

# 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K均值聚类
kmeans = KMeans(n_clusters=4, random_state=42)
kmeans_labels = kmeans.fit_predict(X_scaled)

# DBSCAN聚类
dbscan = DBSCAN(eps=0.3, min_samples=5)
dbscan_labels = dbscan.fit_predict(X_scaled)

# 层次聚类
agg_clustering = AgglomerativeClustering(n_clusters=4)
agg_labels = agg_clustering.fit_predict(X_scaled)

# 可视化聚类结果
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.scatter(X[:, 0], X[:, 1], c=kmeans_labels, cmap='viridis', s=50, alpha=0.8)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', marker='X', s=100)
plt.title('K均值聚类')

plt.subplot(1, 3, 2)
plt.scatter(X[:, 0], X[:, 1], c=dbscan_labels, cmap='viridis', s=50, alpha=0.8)
plt.title('DBSCAN聚类')

plt.subplot(1, 3, 3)
plt.scatter(X[:, 0], X[:, 1], c=agg_labels, cmap='viridis', s=50, alpha=0.8)
plt.title('层次聚类')

plt.tight_layout()
plt.savefig('clustering.png', dpi=300)
plt.close()

# 生成非线性数据
X, y = make_moons(n_samples=500, noise=0.1, random_state=42)

# 降维
pca = PCA(n_components=2)
tsne = TSNE(n_components=2, random_state=42)

X_pca = pca.fit_transform(X)
X_tsne = tsne.fit_transform(X)

# 可视化降维结果
plt.figure(figsize=(12, 5))

plt.subplot(1, 3, 1)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', s=50, alpha=0.8)
plt.title('原始数据')

plt.subplot(1, 3, 2)
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', s=50, alpha=0.8)
plt.title('PCA降维')

plt.subplot(1, 3, 3)
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='viridis', s=50, alpha=0.8)
plt.title('t-SNE降维')

plt.tight_layout()
plt.savefig('dimensionality_reduction.png', dpi=300)
plt.close()

# 人脸数据集降维示例
faces = fetch_olivetti_faces()
X = faces.data
y = faces.target

# 使用PCA降维
pca = PCA(n_components=100)
X_pca = pca.fit_transform(X)

# 重建人脸
X_reconstructed = pca.inverse_transform(X_pca)

# 可视化原始人脸和重建人脸
plt.figure(figsize=(10, 5))

for i in range(10):
    plt.subplot(2, 10, i + 1)
    plt.imshow(X[i].reshape(64, 64), cmap='gray')
    plt.axis('off')
    if i == 0:
        plt.title('原始人脸')
    
    plt.subplot(2, 10, i + 11)
    plt.imshow(X_reconstructed[i].reshape(64, 64), cmap='gray')
    plt.axis('off')
    if i == 0:
        plt.title('PCA重建人脸')

plt.tight_layout()
plt.savefig('face_reconstruction.png', dpi=300)
plt.close()

# 可视化PCA解释方差比
plt.figure(figsize=(10, 6))
plt.plot(np.cumsum(pca.explained_variance_ratio_), marker='o')
plt.xlabel('主成分数量')
plt.ylabel('解释方差比例')
plt.title('PCA解释方差比例累积图')
plt.grid(True)
plt.savefig('pca_variance.png', dpi=300)
plt.close()
```

## 深度学习入门

Python的TensorFlow和PyTorch是两个主流的深度学习框架。

### TensorFlow/PyTorch基础

```python
# TensorFlow基础示例
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import numpy as np

# 加载MNIST数据集
(X_train, y_train), (X_test, y_test) = mnist.load_data()

# 数据预处理
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)

# 构建CNN模型
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(10, activation='softmax')
])

# 编译模型
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 打印模型结构
model.summary()

# 训练模型
history = model.fit(X_train, y_train, epochs=5, batch_size=128, 
                    validation_split=0.2, verbose=1)

# 评估模型
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"测试集准确率: {test_acc:.4f}")

# 可视化训练过程
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='训练准确率')
plt.plot(history.history['val_accuracy'], label='验证准确率')
plt.title('模型准确率')
plt.xlabel('Epoch')
plt.ylabel('准确率')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='训练损失')
plt.plot(history.history['val_loss'], label='验证损失')
plt.title('模型损失')
plt.xlabel('Epoch')
plt.ylabel('损失')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png', dpi=300)
plt.close()

# 预测并可视化结果
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

# 显示一些预测结果
plt.figure(figsize=(12, 8))
for i in range(15):
    plt.subplot(3, 5, i+1)
    plt.imshow(X_test[i].reshape(28, 28), cmap='gray')
    plt.title(f'真实: {y_true[i]}, 预测: {y_pred_classes[i]}')
    plt.axis('off')
plt.tight_layout()
plt.savefig('prediction_results.png', dpi=300)
plt.close()
```

# PyTorch基础示例
```python
# PyTorch基础示例
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'使用设备: {device}')

# 数据预处理
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# 加载MNIST数据集
train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=64, shuffle=False)

# 定义CNN模型
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = nn.functional.relu(x)
        x = self.conv2(x)
        x = nn.functional.relu(x)
        x = nn.functional.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = nn.functional.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = nn.functional.log_softmax(x, dim=1)
        return output

# 实例化模型
model = CNN().to(device)
print(model)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
def train(model, device, train_loader, optimizer, epoch):
    model.train()
    train_loss = 0
    correct = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        
        if batch_idx % 100 == 0:
            print(f'Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                  f'({100. * batch_idx / len(train_loader):.0f}%)], '
                  f'Loss: {loss.item():.6f}')
    
    train_loss /= len(train_loader.dataset)
    accuracy = 100. * correct / len(train_loader.dataset)
    print(f'训练集: 平均损失: {train_loss:.4f}, 准确率: {correct}/{len(train_loader.dataset)} ({accuracy:.2f}%)')
    return train_loss, accuracy

# 测试模型
def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    
    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    print(f'测试集: 平均损失: {test_loss:.4f}, 准确率: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)')
    return test_loss, accuracy

# 训练和测试
epochs = 5
train_losses = []
train_accs = []
test_losses = []
test_accs = []

for epoch in range(1, epochs + 1):
    train_loss, train_acc = train(model, device, train_loader, optimizer, epoch)
    test_loss, test_acc = test(model, device, test_loader)
    
    train_losses.append(train_loss)
    train_accs.append(train_acc)
    test_losses.append(test_loss)
    test_accs.append(test_acc)

# 可视化训练过程
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(range(1, epochs + 1), train_accs, label='训练准确率')
plt.plot(range(1, epochs + 1), test_accs, label='测试准确率')
plt.title('模型准确率')
plt.xlabel('Epoch')
plt.ylabel('准确率 (%)')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(range(1, epochs + 1), train_losses, label='训练损失')
plt.plot(range(1, epochs + 1), test_losses, label='测试损失')
plt.title('模型损失')
plt.xlabel('Epoch')
plt.ylabel('损失')
plt.legend()

plt.tight_layout()
plt.savefig('pytorch_training.png', dpi=300)
plt.close()

# 保存模型
torch.save(model.state_dict(), 'mnist_cnn.pt')
print('模型已保存')
```

## 人工智能应用

人工智能技术已经广泛应用于各个领域，Python是开发AI应用的首选语言。

### 图像识别

```python
# 图像识别示例 - 使用预训练的ResNet模型
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# 加载预训练的ResNet50模型
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
model.eval()

# 图像预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 加载ImageNet类别标签
with open('imagenet_classes.txt') as f:
    categories = [s.strip() for s in f.readlines()]

# 图像识别函数
def predict_image(image_path):
    image = Image.open(image_path)
    image_tensor = preprocess(image).unsqueeze(0)  # 添加批次维度
    
    with torch.no_grad():
        output = model(image_tensor)
    
    # 获取前5个预测结果
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    
    # 显示图像和预测结果
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.axis('off')
    plt.title('输入图像')
    
    plt.subplot(1, 2, 2)
    y = np.arange(5)
    plt.grid(axis='x')
    plt.barh(y, top5_prob.numpy())
    plt.yticks(y, [categories[idx] for idx in top5_catid.numpy()])
    plt.xlabel('概率')
    plt.title('预测结果')
    
    plt.tight_layout()
    plt.savefig('image_recognition_result.png', dpi=300)
    plt.close()
    
    # 打印预测结果
    for i in range(5):
        print(f"{categories[top5_catid[i]]} ({top5_prob[i]:.2%})")

# 使用示例
predict_image('example_image.jpg')
```

### 自然语言处理

```python
# 自然语言处理示例 - 使用NLTK和Transformers
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# 下载必要的NLTK资源
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 文本预处理函数
def preprocess_text(text):
    # 分句
    sentences = sent_tokenize(text)
    
    # 分词、去除标点和停用词、词形还原
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    processed_sentences = []
    tokens_list = []
    
    for sentence in sentences:
        # 分词
        tokens = word_tokenize(sentence.lower())
        
        # 去除标点和停用词
        tokens = [token for token in tokens if token not in string.punctuation and token not in stop_words]
        
        # 词形还原
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        if tokens:
            processed_sentences.append(' '.join(tokens))
            tokens_list.extend(tokens)
    
    return processed_sentences, tokens_list

# 文本分析示例
sample_text = """
自然语言处理（NLP）是人工智能的一个子领域，专注于计算机与人类语言之间的交互。
它结合了计算机科学、人工智能和语言学，使计算机能够理解、解释和生成人类语言。
自然语言处理的应用非常广泛，包括机器翻译、情感分析、文本摘要、问答系统等。
随着深度学习技术的发展，特别是Transformer模型的出现，NLP领域取得了巨大的进步。
现在，像BERT、GPT等预训练模型已经能够理解上下文并生成高质量的文本。
"""

# 预处理文本
processed_sentences, tokens = preprocess_text(sample_text)

# 词频统计
word_freq = Counter(tokens)
most_common_words = word_freq.most_common(10)

# 可视化词频
plt.figure(figsize=(10, 6))
plt.bar([word for word, freq in most_common_words], [freq for word, freq in most_common_words])
plt.title('最常见的10个词')
plt.xlabel('词')
plt.ylabel('频率')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('word_frequency.png', dpi=300)
plt.close()

# 生成词云
wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(' '.join(tokens))
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('词云')
plt.savefig('wordcloud.png', dpi=300)
plt.close()

# 使用Transformers进行情感分析
from transformers import pipeline

# 初始化情感分析管道
sentiment_analyzer = pipeline('sentiment-analysis')

# 分析文本情感
sentences = [
    "I love this product, it's amazing!",
    "The service was terrible and the staff was rude.",
    "The movie was okay, not great but not bad either."
]

for sentence in sentences:
    result = sentiment_analyzer(sentence)
    print(f"文本: '{sentence}'")
    print(f"情感: {result[0]['label']}, 置信度: {result[0]['score']:.4f}\n")
```

### 推荐系统

```python
# 推荐系统示例 - 协同过滤
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

# 创建用户-物品评分矩阵
ratings_data = {
    'User1': {'Item1': 5, 'Item2': 4, 'Item3': 0, 'Item4': 1, 'Item5': 0},
    'User2': {'Item1': 0, 'Item2': 0, 'Item3': 5, 'Item4': 4, 'Item5': 0},
    'User3': {'Item1': 1, 'Item2': 1, 'Item3': 0, 'Item4': 5, 'Item5': 4},
    'User4': {'Item1': 0, 'Item2': 0, 'Item3': 4, 'Item4': 0, 'Item5': 5},
    'User5': {'Item1': 4, 'Item2': 5, 'Item3': 0, 'Item4': 0, 'Item5': 0},
}

ratings_df = pd.DataFrame(ratings_data).T.fillna(0)
print("用户-物品评分矩阵:")
print(ratings_df)

# 基于用户的协同过滤
def user_based_cf(ratings, user_id, k=2, n_items=2):
    # 计算用户相似度
    user_similarity = cosine_similarity(ratings)
    user_similarity_df = pd.DataFrame(user_similarity, index=ratings.index, columns=ratings.index)
    print(f"\n用户 {user_id} 与其他用户的相似度:")
    print(user_similarity_df.loc[user_id].sort_values(ascending=False))
    
    # 找到最相似的k个用户
    similar_users = user_similarity_df.loc[user_id].sort_values(ascending=False)[1:k+1].index
    print(f"\n与用户 {user_id} 最相似的 {k} 个用户: {list(similar_users)}")
    
    # 为用户推荐物品
    user_ratings = ratings.loc[user_id]
    similar_users_ratings = ratings.loc[similar_users]
    
    # 找出用户未评分的物品
    unrated_items = user_ratings[user_ratings == 0].index
    
    # 计算预测评分
    predicted_ratings = {}
    for item in unrated_items:
        item_ratings = similar_users_ratings[item]
        if item_ratings.sum() > 0:  # 确保至少有一个相似用户评价过该物品
            predicted_rating = item_ratings.mean()
            predicted_ratings[item] = predicted_rating
    
    # 推荐评分最高的n个物品
    recommendations = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:n_items]
    return recommendations

# 基于物品的协同过滤
def item_based_cf(ratings, user_id, n_items=2):
    # 计算物品相似度
    item_similarity = cosine_similarity(ratings.T)
    item_similarity_df = pd.DataFrame(item_similarity, index=ratings.columns, columns=ratings.columns)
    
    # 为用户推荐物品
    user_ratings = ratings.loc[user_id]
    
    # 找出用户未评分的物品
    unrated_items = user_ratings[user_ratings == 0].index
    
    # 找出用户已评分的物品
    rated_items = user_ratings[user_ratings > 0].index
    
    # 计算预测评分
    predicted_ratings = {}
    for unrated_item in unrated_items:
        predicted_rating = 0
        similarity_sum = 0
        
        for rated_item in rated_items:
            similarity = item_similarity_df.loc[unrated_item, rated_item]
            user_rating = user_ratings[rated_item]
            
            predicted_rating += similarity * user_rating
            similarity_sum += similarity
        
        if similarity_sum > 0:
            predicted_ratings[unrated_item] = predicted_rating / similarity_sum
    
    # 推荐评分最高的n个物品
    recommendations = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:n_items]
    return recommendations

# 为用户生成推荐
user_id = 'User1'
user_based_recommendations = user_based_cf(ratings_df, user_id)
item_based_recommendations = item_based_cf(ratings_df, user_id)

print(f"\n基于用户的协同过滤为 {user_id} 推荐的物品:")
for item, rating in user_based_recommendations:
    print(f"{item}: 预测评分 {rating:.2f}")

print(f"\n基于物品的协同过滤为 {user_id} 推荐的物品:")
for item, rating in item_based_recommendations:
    print(f"{item}: 预测评分 {rating:.2f}")

# 可视化用户相似度
plt.figure(figsize=(10, 8))
plt.imshow(cosine_similarity(ratings_df), cmap='viridis')
plt.colorbar(label='余弦相似度')
plt.xticks(range(len(ratings_df.index)), ratings_df.index, rotation=45)
plt.yticks(range(len(ratings_df.index)), ratings_df.index)
plt.title('用户相似度热图')
plt.tight_layout()
plt.savefig('user_similarity.png', dpi=300)
plt.close()
```

## 总结

Python高级架构模块涵盖了从微信小程序到人工智能的多种高级应用开发技能。通过学习这些内容，你将能够设计和构建可扩展、可维护的企业级应用，满足现代软件开发的需求。

无论是构建Web应用、开发爬虫系统、进行数据分析，还是实现人工智能应用，Python都提供了强大的工具和库支持。掌握这些技术，将使你在软件开发领域具备竞争力，能够应对各种复杂的开发挑战。