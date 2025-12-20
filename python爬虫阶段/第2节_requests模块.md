# 第2节：requests模块

## 学习目标

- **<font color="red">掌握requests库的安装与基本使用</font>**
- **<font color="blue">理解headers参数的作用与配置方法</font>**
- **<font color="green">学习发送带参数的请求</font>**
- **<font color="purple">掌握cookie的基本使用方法</font>**
- **<font color="orange">了解常见的反爬机制与应对策略</font>**

## 知识点

### requests库基础

- **<font color="red">安装方法</font>**：`pip install requests`
- **<font color="blue">主要功能</font>**：发送HTTP请求，获取响应数据
- **<font color="green">核心方法</font>**：
  - `requests.get()` - 发送GET请求
  - `requests.post()` - 发送POST请求
  - `requests.put()` - 发送PUT请求
  - `requests.delete()` - 发送DELETE请求

### headers参数配置

- **<font color="red">作用</font>**：模拟浏览器行为，绕过基本反爬机制
- **<font color="blue">常用字段</font>**：
  - `User-Agent` - 浏览器标识
  - `Referer` - 请求来源页面
  - `Cookie` - 存储用户状态信息
  - `Host` - 目标主机
  - `Accept` - 接受的内容类型

### 发送带参数的请求

- **<font color="red">GET请求参数</font>**：使用`params`参数传递
- **<font color="blue">POST请求参数</font>**：
  - `data` - 表单数据
  - `json` - JSON格式数据
- **<font color="green">文件上传</font>**：使用`files`参数

### cookie的使用

- **<font color="red">获取方式</font>**：
  - 从响应中提取：`response.cookies`
  - 手动设置：在headers中添加Cookie字段
- **<font color="blue">会话维持</font>**：使用`requests.Session()`
- **<font color="green">cookie操作</font>**：
  - 读取：`session.cookies['cookie_name']`
  - 设置：`session.cookies.set('cookie_name', 'value')`

### 反爬机制与应对

- **<font color="red">基于User-Agent的反爬</font>**：
  - 策略：设置随机User-Agent
- **<font color="blue">基于IP的反爬</font>**：
  - 策略：使用代理IP、控制请求频率
- **<font color="green">基于Cookie的反爬</font>**：
  - 策略：维持会话状态、模拟登录

## 典型示例

### 基本GET请求

```python
import requests

# 发送GET请求
url = 'https://www.example.com'
response = requests.get(url)

# 查看响应状态码
print(f'状态码: {response.status_code}')

# 查看响应内容
print(f'响应内容: {response.text[:100]}...')

# 查看响应头
print(f'响应头: {response.headers}')
```

### 设置请求头

```python
import requests

# 定义headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.example.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

# 发送带headers的请求
url = 'https://www.example.com'
response = requests.get(url, headers=headers)

print(f'状态码: {response.status_code}')
```

### 发送带参数的GET请求

```python
import requests

# 定义请求参数
params = {
    'q': 'python爬虫',
    'page': 1
}

# 发送带参数的GET请求
url = 'https://www.example.com/search'
response = requests.get(url, params=params)

# 查看实际请求的URL
print(f'请求URL: {response.url}')
print(f'状态码: {response.status_code}')
```

### 发送POST请求

```python
import requests

# 定义表单数据
data = {
    'username': 'test_user',
    'password': 'test_password'
}

# 发送POST请求
url = 'https://www.example.com/login'
response = requests.post(url, data=data)

print(f'状态码: {response.status_code}')
print(f'响应内容: {response.text[:100]}...')
```

### 使用Session维持会话

```python
import requests

# 创建会话对象
session = requests.Session()

# 设置会话级别的headers
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# 登录
login_url = 'https://www.example.com/login'
login_data = {'username': 'test_user', 'password': 'test_password'}
login_response = session.post(login_url, data=login_data)

# 访问需要登录的页面
protected_url = 'https://www.example.com/profile'
profile_response = session.get(protected_url)

print(f'登录状态码: {login_response.status_code}')
print(f'个人页面状态码: {profile_response.status_code}')
```

## 实际示例

### 爬取百度搜索结果

```python
import requests

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

# 设置搜索参数
params = {
    'wd': 'Python爬虫教程',
    'pn': 0  # 页码，0表示第一页
}

# 发送请求
url = 'https://www.baidu.com/s'
response = requests.get(url, headers=headers, params=params)

# 检查响应
if response.status_code == 200:
    print(f'成功获取搜索结果，内容长度: {len(response.text)}字节')
    # 这里可以使用BeautifulSoup或正则表达式提取搜索结果
else:
    print(f'请求失败，状态码: {response.status_code}')
```

## 思考题

1. 为什么有时候需要使用Session而不是单独的请求？
2. 如何处理网站的登录验证码问题？
3. requests库相比urllib有哪些优势？
4. 如何处理HTTPS网站的证书验证问题？
5. 如何设计一个随机User-Agent池来避免被反爬？

## 小结

- **<font color="red">requests库是Python中最流行的HTTP客户端库，简化了HTTP请求的发送和处理</font>**
- **<font color="blue">合理设置headers可以有效绕过基本的反爬机制</font>**
- **<font color="green">GET和POST是最常用的请求方法，分别用于获取资源和提交数据</font>**
- **<font color="purple">Session对象可以维持会话状态，适用于需要登录的网站爬取</font>**
- **<font color="orange">了解并应对常见的反爬机制是成功爬取数据的关键</font>**

## 总结

requests模块是Python爬虫开发中最基础也是最重要的工具之一。本节课介绍了requests库的安装和基本使用方法，包括发送各种类型的HTTP请求、设置请求头、处理请求参数、维持会话状态等核心功能。通过掌握这些基础知识，我们可以应对大多数网站的基本爬取需求。在实际开发中，还需要根据目标网站的特点，灵活运用各种技巧来绕过反爬机制，提高爬取效率和成功率。