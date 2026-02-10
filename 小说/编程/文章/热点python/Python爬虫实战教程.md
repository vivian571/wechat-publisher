  # 【震惊】10分钟学会Python爬虫，小白也能轻松获取网页数据！

![爬虫概念图](https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="red">Python爬虫到底是什么？简单说就是用代码自动获取网页上的信息，比人工复制粘贴快100倍！</font>**

![数据抓取](https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="blue">想想看，你是想花一整天手动复制网页数据，还是喝杯咖啡的功夫就能自动获取上千条信息？</font>**

![编程效率](https://images.unsplash.com/photo-1522252234503-e356532cafd5?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="green">今天我就教你用Python两大神器——requests和BeautifulSoup，轻松实现网页数据抓取！</font>**

![工具展示](https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="purple">不懂编程？没关系！跟着我的步骤来，保证你能快速上手！</font>**

![学习过程](https://images.unsplash.com/photo-1517694712202-14dd9538aa97?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="orange">首先，我们需要安装两个超级实用的库，复制下面的命令到你的终端运行就行：</font>**

```python
pip install requests beautifulsoup4
```

![安装过程](https://images.unsplash.com/photo-1515879218367-8466d910aaa4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="red">requests库就像你的浏览器，负责发送请求获取网页内容；BeautifulSoup则像你的眼睛，帮你从网页中找到需要的信息！</font>**

![网页请求](https://images.unsplash.com/photo-1484417894907-623942c8ee29?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="blue">先来看看requests怎么用，超简单的三行代码就能获取整个网页：</font>**

```python
import requests

# 发送GET请求获取网页内容
response = requests.get('https://www.example.com')
print(f'状态码: {response.status_code}')
print(response.text[:100])  # 打印前100个字符
```

![请求结果](https://images.unsplash.com/photo-1507721999472-8ed4421c4af2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="green">但等等，很多网站会拒绝机器人访问，所以我们需要伪装成真人，只需添加一个headers参数：</font>**

```python
# 设置请求头，伪装成浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 带headers的请求
response = requests.get('https://www.example.com', headers=headers)
```

![伪装请求](https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="purple">现在我们有了网页内容，但它是一大堆HTML代码，怎么找到我们想要的信息呢？这时候BeautifulSoup就派上用场了！</font>**

![数据解析](https://images.unsplash.com/photo-1515879218367-8466d910aaa4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="orange">BeautifulSoup就像一把瑞士军刀，可以精确定位并提取网页中的任何元素：</font>**

```python
from bs4 import BeautifulSoup

# 创建BeautifulSoup对象
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有标题
titles = soup.find_all('h2')
for title in titles:
    print(title.text.strip())

# 找到特定class的元素
articles = soup.find_all('div', class_='article')
for article in articles:
    print(article.text.strip()[:50] + '...')
```

![元素提取](https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="red">还可以使用CSS选择器，就像在前端开发中一样，超级直观：</font>**

```python
# 使用CSS选择器查找元素
headlines = soup.select('.headline')
for headline in headlines:
    print(headline.text)

# 查找所有链接
links = soup.select('a[href]')
for link in links:
    print(f'链接文本: {link.text}, URL: {link["href"]}')
```

![CSS选择器](https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="blue">现在，让我们结合requests和BeautifulSoup，写一个完整的爬虫实例，爬取一个电影网站的信息：</font>**

```python
import requests
from bs4 import BeautifulSoup
import time

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 目标URL
url = 'https://movie.example.com/top250'

# 发送请求
response = requests.get(url, headers=headers)

# 确保请求成功
if response.status_code == 200:
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到所有电影条目
    movies = soup.select('.movie-item')
    
    # 遍历并提取信息
    for movie in movies:
        # 提取标题
        title = movie.select_one('.title').text.strip()
        
        # 提取评分
        rating = movie.select_one('.rating').text.strip()
        
        # 提取简介
        intro = movie.select_one('.intro').text.strip()
        
        # 打印结果
        print(f'电影: {title}')
        print(f'评分: {rating}')
        print(f'简介: {intro[:50]}...')
        print('-' * 50)
        
        # 休息一下，避免请求过快
        time.sleep(1)
else:
    print(f'请求失败，状态码: {response.status_code}')
```

![完整实例](https://images.unsplash.com/photo-1489875347897-49f64b51c1f8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="green">怎么样，是不是超级简单？但要注意，爬虫也有一些注意事项：</font>**

![注意事项](https://images.unsplash.com/photo-1555099962-4199c345e5dd?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="purple">1. 遵守robots.txt规则，不要爬取网站明确禁止的内容</font>**

![robots规则](https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="orange">2. 控制爬取速度，添加time.sleep()避免对服务器造成压力</font>**

![速度控制](https://images.unsplash.com/photo-1504639725590-34d0984388bd?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="red">3. 处理异常情况，网络可能会断开或网站结构可能会变化</font>**

```python
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # 如果状态码不是200，抛出异常
except requests.exceptions.RequestException as e:
    print(f'请求出错: {e}')
```

![异常处理](https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="blue">4. 数据存储，将爬取的数据保存到文件或数据库中：</font>**

```python
import csv

# 保存到CSV文件
with open('movies.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['标题', '评分', '简介'])  # 写入表头
    
    for movie in movies:
        title = movie.select_one('.title').text.strip()
        rating = movie.select_one('.rating').text.strip()
        intro = movie.select_one('.intro').text.strip()
        
        writer.writerow([title, rating, intro])
```

![数据存储](https://images.unsplash.com/photo-1544383835-bda2bc66a55d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="green">掌握了这些基础知识，你已经可以开发出实用的爬虫程序了！想爬取哪个网站的数据，完全由你决定！</font>**

![成果展示](https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="purple">如果遇到更复杂的网站，可能需要处理JavaScript渲染的内容，这时可以考虑使用Selenium等更高级的工具。</font>**

![高级工具](https://images.unsplash.com/photo-1527689368864-3a821dbccc34?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="orange">总之，Python爬虫入门其实很简单，掌握requests和BeautifulSoup这两个库就能解决大部分问题！</font>**

![总结](https://images.unsplash.com/photo-1515879218367-8466d910aaa4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

**<font color="red">快动手试试吧，你会发现编写爬虫程序既有趣又实用，能大大提高你的工作效率！</font>**

![行动号召](https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)