# 第4节：BeautifulSoup

## 学习目标

- **<font color="red">掌握BeautifulSoup的基本用法</font>**
- **<font color="blue">学习HTML文档的解析方法</font>**
- **<font color="green">理解CSS选择器和XPath的应用</font>**
- **<font color="purple">熟练使用find和find_all方法提取数据</font>**
- **<font color="orange">掌握节点遍历和属性操作的技巧</font>**

## 知识点

### BeautifulSoup基础

- **<font color="red">定义</font>**：Python的HTML/XML解析库
- **<font color="blue">作用</font>**：从HTML或XML文件中提取数据
- **<font color="green">安装方法</font>**：`pip install beautifulsoup4`
- **<font color="purple">解析器选择</font>**：
  - `html.parser`：Python标准库解析器
  - `lxml`：速度快，需额外安装
  - `html5lib`：最接近浏览器的解析方式

### 创建BeautifulSoup对象

- **<font color="red">从字符串创建</font>**：
  ```python
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(html_doc, 'html.parser')
  ```

- **<font color="blue">从文件创建</font>**：
  ```python
  with open('index.html') as f:
      soup = BeautifulSoup(f, 'html.parser')
  ```

- **<font color="green">从URL创建</font>**：
  ```python
  import requests
  from bs4 import BeautifulSoup
  
  response = requests.get('https://example.com')
  soup = BeautifulSoup(response.text, 'html.parser')
  ```

### 节点选择方法

- **<font color="red">按标签名查找</font>**：
  - `soup.title`：获取title标签
  - `soup.p`：获取第一个p标签

- **<font color="blue">按属性查找</font>**：
  - `soup.find(id="link1")`：查找id为link1的元素
  - `soup.find(class_="sidebar")`：查找class为sidebar的元素

- **<font color="green">按CSS选择器查找</font>**：
  - `soup.select("div.content")`：查找class为content的div元素
  - `soup.select("#main p")`：查找id为main的元素下的所有p元素

- **<font color="purple">按XPath查找</font>**（需配合lxml）：
  ```python
  from lxml import etree
  html = etree.HTML(str(soup))
  result = html.xpath('//div[@class="content"]/p/text()')
  ```

### 常用查找方法

- **<font color="red">find()</font>**：
  - 查找第一个匹配的标签
  - 参数：name, attrs, recursive, string, **kwargs

- **<font color="blue">find_all()</font>**：
  - 查找所有匹配的标签
  - 参数：name, attrs, recursive, string, limit, **kwargs

- **<font color="green">find_parent()/find_parents()</font>**：
  - 查找父节点/所有父节点

- **<font color="purple">find_next_sibling()/find_next_siblings()</font>**：
  - 查找下一个兄弟节点/所有后续兄弟节点

- **<font color="orange">find_previous_sibling()/find_previous_siblings()</font>**：
  - 查找上一个兄弟节点/所有前置兄弟节点

### 节点内容和属性

- **<font color="red">获取文本内容</font>**：
  - `.string`：获取标签的文本内容（只适用于没有子标签的节点）
  - `.text`：获取标签及其子标签的所有文本内容
  - `.get_text()`：获取所有文本，可设置分隔符等参数

- **<font color="blue">获取属性</font>**：
  - `.attrs`：获取所有属性的字典
  - `["attribute"]`：获取特定属性值，如`tag["href"]`
  - `.get("attribute")`：安全获取属性，不存在返回None

- **<font color="green">修改内容和属性</font>**：
  - `.string = "新内容"`：修改文本内容
  - `["attribute"] = "新值"`：修改属性值

## 典型示例

### 基本解析示例

```python
# 创建BeautifulSoup对象并解析HTML
from bs4 import BeautifulSoup

html_doc = """
<html>
<head>
    <title>BeautifulSoup示例</title>
</head>
<body>
    <h1>BeautifulSoup教程</h1>
    <p class="intro">BeautifulSoup是一个强大的HTML解析库</p>
    <div id="content">
        <p>它可以帮助我们从HTML中提取数据</p>
        <p>支持多种解析器</p>
    </div>
    <a href="https://example.com" id="link1">示例链接</a>
</body>
</html>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# 获取标题
print(f"标题: {soup.title.string}")

# 获取h1标签
print(f"h1内容: {soup.h1.string}")

# 获取第一个p标签
print(f"第一个p标签: {soup.p.string}")

# 获取id为content的div
content_div = soup.find(id="content")
print(f"content div的内容: {content_div.text.strip()}")

# 获取所有p标签
all_p = soup.find_all('p')
print(f"共找到{len(all_p)}个p标签")
for i, p in enumerate(all_p, 1):
    print(f"第{i}个p标签内容: {p.text.strip()}")
```

### 使用CSS选择器

```python
from bs4 import BeautifulSoup

# 使用上面的html_doc
soup = BeautifulSoup(html_doc, 'html.parser')

# 使用CSS选择器查找元素
intro_p = soup.select(".intro")  # 查找class为intro的元素
print(f"class为intro的元素: {intro_p[0].text}")

# 查找id为content的div下的所有p元素
content_ps = soup.select("#content p")
print(f"content下的p元素数量: {len(content_ps)}")
for p in content_ps:
    print(f"- {p.text}")

# 查找所有链接
links = soup.select("a[href]")  # 查找有href属性的a标签
for link in links:
    print(f"链接文本: {link.text}, URL: {link['href']}")
```

### 遍历文档树

```python
from bs4 import BeautifulSoup

# 使用上面的html_doc
soup = BeautifulSoup(html_doc, 'html.parser')

# 向下遍历
body = soup.body
print("Body的直接子节点:")
for child in body.children:
    if child.name:  # 过滤掉NavigableString
        print(f"- {child.name}")

# 向上遍历
p_intro = soup.find("p", class_="intro")
print(f"p.intro的父节点: {p_intro.parent.name}")

# 平行遍历
content_div = soup.find(id="content")
print("content_div的下一个兄弟节点:")
next_sibling = content_div.find_next_sibling()
if next_sibling:
    print(f"- {next_sibling.name}: {next_sibling.text.strip()}")
```

## 实际示例

### 提取新闻网站的标题和摘要

```python
import requests
from bs4 import BeautifulSoup

# 获取网页内容
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get('https://news.example.com', headers=headers)
html = response.text

# 创建BeautifulSoup对象
soup = BeautifulSoup(html, 'html.parser')

# 假设新闻标题在h2标签中，class为title
news_titles = soup.find_all('h2', class_='title')

# 假设新闻摘要在p标签中，class为summary
news_summaries = soup.find_all('p', class_='summary')

# 打印结果
print(f"找到{len(news_titles)}条新闻:")
for i, (title, summary) in enumerate(zip(news_titles, news_summaries), 1):
    print(f"\n新闻{i}:")
    print(f"标题: {title.text.strip()}")
    print(f"摘要: {summary.text.strip()}")
    
    # 如果标题是链接，提取链接地址
    link = title.find('a')
    if link and 'href' in link.attrs:
        print(f"链接: {link['href']}")
    print("-" * 50)
```

### 提取电商网站的商品信息

```python
import requests
from bs4 import BeautifulSoup

# 获取网页内容
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get('https://shop.example.com/products', headers=headers)
html = response.text

# 创建BeautifulSoup对象
soup = BeautifulSoup(html, 'html.parser')

# 假设商品信息在div标签中，class为product-item
product_items = soup.find_all('div', class_='product-item')

print(f"找到{len(product_items)}个商品:")
for i, product in enumerate(product_items, 1):
    print(f"\n商品{i}:")
    
    # 提取商品名称
    name_tag = product.find('h3', class_='product-name')
    if name_tag:
        print(f"名称: {name_tag.text.strip()}")
    
    # 提取商品价格
    price_tag = product.find('span', class_='product-price')
    if price_tag:
        print(f"价格: {price_tag.text.strip()}")
    
    # 提取商品图片
    img_tag = product.find('img')
    if img_tag and 'src' in img_tag.attrs:
        print(f"图片URL: {img_tag['src']}")
    
    # 提取商品链接
    link_tag = product.find('a', class_='product-link')
    if link_tag and 'href' in link_tag.attrs:
        print(f"详情链接: {link_tag['href']}")
    
    print("-" * 50)
```

## 思考题

1. BeautifulSoup与正则表达式相比，各有什么优缺点？在什么情况下应该选择使用BeautifulSoup？
2. 如何结合CSS选择器和正则表达式，实现更精确的数据提取？
3. 在处理大型HTML文档时，如何优化BeautifulSoup的性能？
4. 如何处理JavaScript动态生成的内容？BeautifulSoup能解决这个问题吗？
5. 如何使用BeautifulSoup修改HTML文档并保存？

## 小结

- **<font color="red">BeautifulSoup是一个强大的HTML/XML解析库，提供了简单的API</font>**
- **<font color="blue">find和find_all方法是最常用的数据提取方法</font>**
- **<font color="green">CSS选择器提供了更简洁的元素定位方式</font>**
- **<font color="purple">节点遍历功能可以灵活处理复杂的文档结构</font>**
- **<font color="orange">与requests库结合使用，可以实现完整的网页数据提取</font>**

## 总结

BeautifulSoup是Python爬虫开发中不可或缺的工具，它提供了强大而简单的HTML解析能力。相比正则表达式，BeautifulSoup更适合处理结构化的HTML文档，代码可读性更高，维护成本更低。本节课介绍了BeautifulSoup的基本用法、常用方法和实际应用场景。通过掌握这些知识，我们可以更高效地从网页中提取所需的数据。在实际开发中，BeautifulSoup通常与requests库结合使用，形成完整的网页数据采集解决方案。对于复杂的网页结构，可以结合CSS选择器或XPath表达式，实现更精确的数据定位和提取。