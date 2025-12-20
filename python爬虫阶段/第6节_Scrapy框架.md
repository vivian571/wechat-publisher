# 第6节：Scrapy框架

## 学习目标

- **<font color="red">掌握Scrapy框架的基本架构和工作原理</font>**
- **<font color="blue">学习创建和配置Scrapy爬虫项目的方法</font>**
- **<font color="green">理解Spider、Item和Pipeline的核心概念</font>**
- **<font color="purple">熟练使用选择器提取网页数据</font>**
- **<font color="orange">掌握中间件和分布式爬虫的实现技巧</font>**

## 知识点

### Scrapy基础

- **<font color="red">定义</font>**：一个用Python编写的开源爬虫框架
- **<font color="blue">特点</font>**：
  - 高效且易于扩展
  - 内置异步网络库，处理并发请求
  - 提供完整的爬虫开发流程
- **<font color="green">安装方法</font>**：`pip install scrapy`

### Scrapy架构

- **<font color="red">组件构成</font>**：
  - Engine：引擎，负责控制数据流
  - Scheduler：调度器，负责管理请求队列
  - Downloader：下载器，负责获取网页
  - Spider：爬虫，负责解析网页和提取数据
  - Item Pipeline：管道，负责处理数据
  - Middleware：中间件，负责处理请求和响应

- **<font color="blue">数据流向</font>**：
  1. Engine从Spider获取初始请求
  2. Engine将请求传递给Scheduler
  3. Scheduler将请求返回给Engine
  4. Engine通过Downloader Middleware将请求发送给Downloader
  5. Downloader获取网页并通过Downloader Middleware返回响应给Engine
  6. Engine将响应传递给Spider进行解析
  7. Spider解析响应并返回提取的数据和新的请求给Engine
  8. Engine将提取的数据传递给Item Pipeline
  9. Engine将新的请求传递给Scheduler

### 创建Scrapy项目

- **<font color="red">创建项目</font>**：
  ```bash
  scrapy startproject myproject
  ```

- **<font color="blue">项目结构</font>**：
  ```
  myproject/
  ├── scrapy.cfg            # 项目配置文件
  └── myproject/            # 项目Python模块
      ├── __init__.py
      ├── items.py          # 项目Item定义
      ├── middlewares.py    # 项目中间件
      ├── pipelines.py      # 项目管道
      ├── settings.py       # 项目设置
      └── spiders/          # 爬虫目录
          └── __init__.py
  ```

- **<font color="green">创建爬虫</font>**：
  ```bash
  cd myproject
  scrapy genspider example example.com
  ```

### Spider类

- **<font color="red">基本属性</font>**：
  - `name`：爬虫名称，必须唯一
  - `allowed_domains`：允许爬取的域名列表
  - `start_urls`：起始URL列表

- **<font color="blue">核心方法</font>**：
  - `parse()`：处理响应的默认回调方法
  - `start_requests()`：生成初始请求的方法

- **<font color="green">Spider类型</font>**：
  - Spider：基础爬虫类
  - CrawlSpider：具有规则的爬虫，可以定义链接提取规则
  - XMLFeedSpider：用于解析XML源
  - CSVFeedSpider：用于解析CSV源
  - SitemapSpider：用于爬取网站地图

### 选择器和数据提取

- **<font color="red">Scrapy选择器</font>**：
  - 基于lxml构建
  - 支持XPath和CSS选择器

- **<font color="blue">XPath选择器</font>**：
  ```python
  # 使用XPath选择器
  response.xpath('//h1/text()').get()
  response.xpath('//a/@href').getall()
  ```

- **<font color="green">CSS选择器</font>**：
  ```python
  # 使用CSS选择器
  response.css('h1::text').get()
  response.css('a::attr(href)').getall()
  ```

- **<font color="purple">组合使用</font>**：
  ```python
  # 组合使用XPath和CSS选择器
  response.css('div.quote').xpath('./span/text()').get()
  ```

### Item类

- **<font color="red">定义Item</font>**：
  ```python
  import scrapy
  
  class ProductItem(scrapy.Item):
      name = scrapy.Field()
      price = scrapy.Field()
      description = scrapy.Field()
      url = scrapy.Field()
  ```

- **<font color="blue">使用Item</font>**：
  ```python
  def parse(self, response):
      product = ProductItem()
      product['name'] = response.css('h1::text').get()
      product['price'] = response.css('.price::text').get()
      product['description'] = response.css('.description::text').get()
      product['url'] = response.url
      yield product
  ```

### Item Pipeline

- **<font color="red">定义Pipeline</font>**：
  ```python
  class MyPipeline:
      def process_item(self, item, spider):
          # 处理item
          return item
  ```

- **<font color="blue">Pipeline方法</font>**：
  - `open_spider(spider)`：爬虫启动时调用
  - `process_item(item, spider)`：处理每个item
  - `close_spider(spider)`：爬虫关闭时调用

- **<font color="green">启用Pipeline</font>**：
  ```python
  # 在settings.py中配置
  ITEM_PIPELINES = {
      'myproject.pipelines.MyPipeline': 300,  # 数字表示优先级，越小越先执行
  }
  ```

### 中间件

- **<font color="red">下载器中间件</font>**：
  - 处理请求和响应
  - 可以修改请求头、代理IP等

- **<font color="blue">Spider中间件</font>**：
  - 处理Spider的输入（响应）和输出（items和请求）

- **<font color="green">启用中间件</font>**：
  ```python
  # 在settings.py中配置
  DOWNLOADER_MIDDLEWARES = {
      'myproject.middlewares.MyDownloaderMiddleware': 543,
  }
  
  SPIDER_MIDDLEWARES = {
      'myproject.middlewares.MySpiderMiddleware': 543,
  }
  ```

### 请求和响应

- **<font color="red">Request对象</font>**：
  ```python
  scrapy.Request(url, callback=self.parse, method='GET', headers=None, cookies=None, meta=None, dont_filter=False)
  ```

- **<font color="blue">Response对象</font>**：
  - `url`：响应的URL
  - `status`：HTTP状态码
  - `headers`：响应头
  - `body`：响应体
  - `request`：生成此响应的请求

- **<font color="green">使用meta传递数据</font>**：
  ```python
  def parse(self, response):
      for product_url in response.css('.product a::attr(href)').getall():
          yield scrapy.Request(
              url=product_url,
              callback=self.parse_product,
              meta={'category': response.css('h1::text').get()}
          )
  
  def parse_product(self, response):
      category = response.meta['category']
      # 处理产品页面
  ```

### 运行爬虫

- **<font color="red">命令行运行</font>**：
  ```bash
  scrapy crawl example
  ```

- **<font color="blue">保存结果</font>**：
  ```bash
  scrapy crawl example -o results.json
  scrapy crawl example -o results.csv
  scrapy crawl example -o results.xml
  ```

- **<font color="green">设置参数</font>**：
  ```bash
  scrapy crawl example -s DOWNLOAD_DELAY=2
  ```

- **<font color="purple">调试</font>**：
  ```bash
  scrapy shell "http://example.com"
  ```

### 配置设置

- **<font color="red">常用设置</font>**：
  - `USER_AGENT`：用户代理
  - `ROBOTSTXT_OBEY`：是否遵守robots.txt规则
  - `CONCURRENT_REQUESTS`：并发请求数
  - `DOWNLOAD_DELAY`：下载延迟
  - `COOKIES_ENABLED`：是否启用cookies
  - `DEFAULT_REQUEST_HEADERS`：默认请求头

- **<font color="blue">设置方式</font>**：
  - 在settings.py中设置
  - 在命令行中使用-s参数
  - 在Spider中设置custom_settings

## 典型示例

### 基本爬虫

```python
# spiders/quotes_spider.py
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        # 提取所有引用
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # 提取下一页链接并跟随
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
```

### 使用Item和Pipeline

```python
# items.py
import scrapy

class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

# spiders/quotes_spider.py
import scrapy
from myproject.items import QuoteItem

class QuotesSpider(scrapy.Spider):
    name = "quotes_item"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.css('div.quote'):
            item = QuoteItem()
            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()
            yield item

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

# pipelines.py
class QuotePipeline:
    def process_item(self, item, spider):
        # 清理引用文本中的引号
        if 'text' in item:
            item['text'] = item['text'].strip('"')
        return item

# settings.py中启用Pipeline
ITEM_PIPELINES = {
    'myproject.pipelines.QuotePipeline': 300,
}
```

### 使用CrawlSpider

```python
# spiders/author_spider.py
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from myproject.items import AuthorItem

class AuthorSpider(CrawlSpider):
    name = "authors"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    rules = (
        # 提取并跟随所有作者页面的链接
        Rule(LinkExtractor(allow=r'/author/.*'), callback='parse_author'),
        # 提取并跟随分页链接
        Rule(LinkExtractor(restrict_css='li.next'), follow=True),
    )

    def parse_author(self, response):
        author = AuthorItem()
        author['name'] = response.css('h3.author-title::text').get()
        author['birth_date'] = response.css('span.author-born-date::text').get()
        author['bio'] = response.css('div.author-description::text').get().strip()
        yield author
```

## 实际示例

### 爬取新闻网站

```python
# items.py
import scrapy

class NewsItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    publish_time = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()

# spiders/news_spider.py
import scrapy
from myproject.items import NewsItem
import datetime

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["example-news.com"]
    start_urls = ["https://example-news.com/latest"]

    def parse(self, response):
        # 提取新闻列表页中的新闻链接
        for news_link in response.css('article.news-item a.title::attr(href)').getall():
            yield response.follow(news_link, self.parse_news)

        # 处理分页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_news(self, response):
        news = NewsItem()
        news['title'] = response.css('h1.article-title::text').get()
        news['content'] = ''.join(response.css('div.article-content p::text').getall())
        news['author'] = response.css('span.author-name::text').get()
        
        # 处理发布时间
        time_str = response.css('time::attr(datetime)').get()
        if time_str:
            news['publish_time'] = datetime.datetime.fromisoformat(time_str)
        
        news['category'] = response.css('span.category::text').get()
        news['url'] = response.url
        
        yield news

# pipelines.py
import json
from itemadapter import ItemAdapter

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('news.json', 'w', encoding='utf-8')
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

class NewsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 清理标题中的多余空白
        if adapter.get('title'):
            adapter['title'] = adapter['title'].strip()
        
        # 清理内容中的多余空白
        if adapter.get('content'):
            adapter['content'] = adapter['content'].strip()
        
        # 处理作者信息
        if adapter.get('author'):
            adapter['author'] = adapter['author'].strip()
            if adapter['author'].startswith('By '):
                adapter['author'] = adapter['author'][3:]
        
        return item

# settings.py中启用Pipeline
ITEM_PIPELINES = {
    'myproject.pipelines.NewsPipeline': 300,
    'myproject.pipelines.JsonWriterPipeline': 800,
}
```

### 分布式爬虫

```python
# settings.py
# 启用Scrapy-Redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = 'redis://localhost:6379'

# spiders/distributed_spider.py
from scrapy_redis.spiders import RedisSpider
from myproject.items import ProductItem

class DistributedSpider(RedisSpider):
    name = "distributed"
    redis_key = "distributed:start_urls"

    def parse(self, response):
        # 提取产品信息
        for product in response.css('div.product'):
            item = ProductItem()
            item['name'] = product.css('h2::text').get()
            item['price'] = product.css('span.price::text').get()
            item['url'] = response.urljoin(product.css('a::attr(href)').get())
            yield item

        # 处理分页
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

## 思考题

1. Scrapy框架相比于requests+BeautifulSoup的组合有哪些优势和劣势？
2. 如何在Scrapy中处理需要登录的网站？
3. 如何优化Scrapy爬虫的性能？有哪些常用的优化策略？
4. Scrapy中如何处理JavaScript渲染的页面？
5. 如何设计一个大规模的分布式爬虫系统？需要考虑哪些因素？

## 小结

- **<font color="red">Scrapy是一个功能强大的爬虫框架，提供了完整的数据采集解决方案</font>**
- **<font color="blue">Spider、Item和Pipeline是Scrapy的三个核心组件</font>**
- **<font color="green">选择器提供了便捷的数据提取方式，支持XPath和CSS选择器</font>**
- **<font color="purple">中间件可以灵活处理请求和响应，实现代理、Cookie等功能</font>**
- **<font color="orange">Scrapy可以通过扩展实现分布式爬虫，提高采集效率</font>**

## 总结

Scrapy是Python爬虫开发中最流行的框架之一，它提供了一个完整的爬虫开发环境，包括数据提取、处理和存储等功能。相比于手动组合requests和BeautifulSoup等工具，Scrapy具有更高的开发效率和更好的性能。

本节课介绍了Scrapy的基本架构、核心组件和工作原理，以及如何创建和配置Scrapy项目。通过学习Spider、Item和Pipeline等核心概念，我们可以构建结构化的爬虫程序，实现高效的数据采集。Scrapy的选择器系统提供了强大的数据提取能力，支持XPath和CSS选择器，可以精确定位和提取所需的数据。

在实际开发中，Scrapy可以通过中间件扩展功能，实现代理IP、User-Agent轮换、Cookie管理等功能，有效应对网站的反爬虫措施。对于大规模的爬虫需求，可以结合Redis等工具实现分布式爬虫，提高数据采集的效率和稳定性。

总的来说，Scrapy是一个功能全面、扩展性强的爬虫框架，适合各种规模的爬虫项目。通过掌握Scrapy，我们可以更加高效地开发和维护爬虫程序，实现更加复杂的数据采集需求。