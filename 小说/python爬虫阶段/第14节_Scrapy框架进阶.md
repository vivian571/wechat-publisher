# 第14节：Scrapy框架进阶

## 学习目标

- **<font color="red">深入理解Scrapy框架的优缺点</font>**
- **<font color="blue">掌握Scrapy的运行流程与原理</font>**
- **<font color="green">学习Scrapy数据永久存储方法</font>**
- **<font color="purple">掌握Scrapy高级配置与优化</font>**
- **<font color="orange">了解Scrapy的扩展与中间件开发</font>**

## 知识点

### Scrapy框架优缺点

- **<font color="red">优点</font>**：
  - 高效的异步网络处理架构
  - 内置数据提取工具（XPath、CSS选择器）
  - 可扩展性强，支持中间件和扩展
  - 内置爬虫管理与监控工具
  - 自动处理常见爬虫问题（重试、去重等）

- **<font color="blue">缺点</font>**：
  - 学习曲线较陡峭
  - 不适合小型爬虫任务
  - 默认不支持JavaScript渲染页面
  - 分布式需要额外配置（Scrapy-Redis）
  - 配置较为复杂

### Scrapy运行流程

- **<font color="red">请求生成</font>**：
  - Spider生成初始请求
  - 请求被发送到调度器

- **<font color="blue">调度处理</font>**：
  - 调度器对请求进行去重
  - 按优先级排序请求
  - 将请求发送给下载器

- **<font color="green">下载执行</font>**：
  - 下载器中间件处理请求
  - 下载器获取网页内容
  - 生成响应对象

- **<font color="purple">响应处理</font>**：
  - 下载器中间件处理响应
  - 响应传递给Spider处理
  - Spider解析数据并生成Item

- **<font color="orange">数据处理</font>**：
  - Item传递给Item Pipeline
  - Pipeline进行数据清洗、验证和存储

### 数据永久存储

- **<font color="red">文件存储</font>**：
  - JSON、CSV、XML格式
  - 使用Feed exports功能
  - 自定义Item Exporter

- **<font color="blue">关系型数据库</font>**：
  - MySQL、PostgreSQL、SQLite
  - 使用SQLAlchemy ORM
  - 自定义Pipeline实现

- **<font color="green">NoSQL数据库</font>**：
  - MongoDB、Redis、Elasticsearch
  - 使用专用客户端库
  - 适合非结构化或半结构化数据

- **<font color="purple">分布式存储</font>**：
  - HDFS与Hadoop生态系统
  - 云存储服务（S3、OSS等）

### Scrapy高级配置

- **<font color="red">并发与性能</font>**：
  - CONCURRENT_REQUESTS：并发请求数
  - DOWNLOAD_DELAY：下载延迟
  - CONCURRENT_REQUESTS_PER_DOMAIN：每域名并发数

- **<font color="blue">缓存机制</font>**：
  - HTTPCACHE_ENABLED：启用HTTP缓存
  - HTTPCACHE_EXPIRATION_SECS：缓存过期时间
  - HTTPCACHE_DIR：缓存目录

- **<font color="green">自动限速</font>**：
  - AUTOTHROTTLE_ENABLED：启用自动限速
  - AUTOTHROTTLE_TARGET_CONCURRENCY：目标并发数
  - AUTOTHROTTLE_DEBUG：调试模式

## 典型示例

### 数据存储到MySQL

```python
# pipelines.py
import mysql.connector
from itemadapter import ItemAdapter

class MySQLPipeline:
    def __init__(self):
        # 数据库连接参数
        self.conn = None
        self.cursor = None
        self.db_params = {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'database': 'scrapy_data'
        }
    
    def open_spider(self, spider):
        """爬虫启动时连接数据库"""
        self.conn = mysql.connector.connect(**self.db_params)
        self.cursor = self.conn.cursor()
        # 创建表（如果不存在）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                content TEXT,
                author VARCHAR(100),
                publish_date DATE,
                url VARCHAR(255) UNIQUE
            )
        ''')
        self.conn.commit()
    
    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def process_item(self, item, spider):
        """处理每个爬取到的item"""
        adapter = ItemAdapter(item)
        
        # 准备SQL语句和数据
        sql = '''
            INSERT INTO articles (title, content, author, publish_date, url)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            title=%s, content=%s, author=%s, publish_date=%s
        '''
        
        values = (
            adapter.get('title', ''),
            adapter.get('content', ''),
            adapter.get('author', ''),
            adapter.get('publish_date', None),
            adapter.get('url', ''),
            adapter.get('title', ''),
            adapter.get('content', ''),
            adapter.get('author', ''),
            adapter.get('publish_date', None)
        )
        
        # 执行SQL
        self.cursor.execute(sql, values)
        self.conn.commit()
        
        return item
```

### 数据存储到MongoDB

```python
# pipelines.py
import pymongo
from itemadapter import ItemAdapter

class MongoPipeline:
    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        # 从settings.py获取MongoDB配置
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'scrapy_default')
        )

    def open_spider(self, spider):
        # 连接MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # 创建索引
        self.db[self.collection_name].create_index('url', unique=True)

    def close_spider(self, spider):
        # 关闭MongoDB连接
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        # 将数据插入MongoDB
        adapter = ItemAdapter(item)
        # 使用url作为唯一键，实现更新或插入
        self.db[self.collection_name].update_one(
            {'url': adapter.get('url')},
            {'$set': dict(item)},
            upsert=True
        )
        return item
```

### 自定义中间件处理动态页面

```python
# middlewares.py
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class SeleniumMiddleware:
    def __init__(self):
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        
        # 初始化浏览器
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def __del__(self):
        # 关闭浏览器
        self.driver.quit()
    
    def process_request(self, request, spider):
        # 仅处理标记为需要selenium渲染的请求
        if request.meta.get('selenium', False):
            self.driver.get(request.url)
            
            # 等待页面加载（可根据需要调整）
            time.sleep(2)
            
            # 执行JavaScript脚本（如有需要）
            if 'js_script' in request.meta:
                self.driver.execute_script(request.meta['js_script'])
                time.sleep(1)
            
            # 获取渲染后的页面内容
            body = self.driver.page_source
            
            # 返回HtmlResponse对象
            return HtmlResponse(
                url=request.url,
                body=body,
                encoding='utf-8',
                request=request
            )
```

## 实际示例

### 新闻网站爬虫与数据存储

```python
# spiders/news_spider.py
import scrapy
from datetime import datetime
from scrapy.loader import ItemLoader
from myproject.items import NewsItem

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['example-news.com']
    start_urls = ['https://example-news.com/latest']
    
    # 自定义设置，覆盖项目设置
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ITEM_PIPELINES': {
            'myproject.pipelines.NewsPipeline': 300,
            'myproject.pipelines.MySQLPipeline': 400,
        }
    }
    
    def parse(self, response):
        # 提取新闻列表页中的新闻链接
        news_links = response.css('div.news-item a::attr(href)').getall()
        
        # 处理每个新闻详情页
        for link in news_links:
            yield response.follow(link, self.parse_news)
        
        # 处理分页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_news(self, response):
        # 使用ItemLoader加载数据
        loader = ItemLoader(item=NewsItem(), response=response)
        
        # 提取数据
        loader.add_css('title', 'h1.title::text')
        loader.add_css('content', 'div.article-content')
        loader.add_css('author', 'span.author::text')
        loader.add_css('publish_date', 'span.date::text')
        loader.add_value('url', response.url)
        loader.add_value('crawl_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 返回处理后的Item
        return loader.load_item()

# items.py
import scrapy
from itemloaders.processors import TakeFirst, Join, MapCompose
from datetime import datetime

def parse_date(date_str):
    # 解析日期字符串为日期对象
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except:
        return None

def clean_text(text):
    # 清理文本
    return text.strip()

class NewsItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    content = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=Join('\n')
    )
    author = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    publish_date = scrapy.Field(
        input_processor=MapCompose(clean_text, parse_date),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    crawl_time = scrapy.Field(
        output_processor=TakeFirst()
    )

# pipelines.py
class NewsPipeline:
    def process_item(self, item, spider):
        # 数据清洗和验证
        if not item.get('title'):
            spider.logger.warning(f"标题为空: {item.get('url')}")
        
        if not item.get('content'):
            spider.logger.warning(f"内容为空: {item.get('url')}")
        
        # 内容长度检查
        if len(item.get('content', '')) < 100:
            spider.logger.warning(f"内容过短: {item.get('url')}")
        
        return item
```

## 思考

- **<font color="red">Scrapy框架与其他爬虫方法相比有哪些优势？</font>** Scrapy提供了完整的爬虫生态系统，包括请求处理、数据提取、中间件扩展等，大大简化了复杂爬虫的开发。

- **<font color="blue">如何处理Scrapy中的JavaScript渲染页面？</font>** 可以通过集成Selenium、Splash等工具，或使用scrapy-playwright等扩展来处理JavaScript渲染页面。

- **<font color="green">如何优化Scrapy爬虫的性能？</font>** 调整并发请求数、使用自动限速、实现缓存机制、优化数据处理流程等方式可以提高性能。

- **<font color="purple">Scrapy的分布式爬取如何实现？</font>** 通过Scrapy-Redis扩展可以实现基于Redis的分布式爬虫，多台机器共享请求队列和去重集合。

## 小结

- Scrapy是一个功能强大的爬虫框架，具有高效、可扩展的特点
- 了解Scrapy的运行流程有助于更好地利用和优化框架
- 数据永久存储是爬虫系统的重要组成部分，Scrapy支持多种存储方式
- 合理配置和使用中间件可以扩展Scrapy的功能
- 掌握Scrapy高级特性可以构建更复杂、高效的爬虫系统

## 总结

本节课我们深入学习了Scrapy框架的进阶知识，包括框架的优缺点分析、详细的运行流程、数据永久存储方法以及高级配置与优化技巧。通过实际示例，我们掌握了如何将爬取的数据存储到MySQL和MongoDB等数据库中，以及如何使用自定义中间件处理动态页面。这些知识使我们能够构建更加强大、高效的爬虫系统，为后续的数据分析和应用打下坚实基础。Scrapy框架作为Python爬虫领域的重要工具，掌握其进阶特性对于开发复杂爬虫项目至关重要。