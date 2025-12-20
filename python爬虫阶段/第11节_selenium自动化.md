# 第11节：selenium自动化
## 学习目标

- **<font color="red">掌握Selenium的基本原理和安装配置方法</font>**
- **<font color="blue">学习浏览器驱动的使用和元素定位技巧</font>**
- **<font color="green">理解等待机制和页面交互操作的实现</font>**
- **<font color="purple">掌握表单操作和模拟用户行为的方法</font>**
- **<font color="orange">学习处理多窗口和iframe的技巧</font>**

## 语法

### 安装与配置

- **<font color="red">安装Selenium</font>**：
  ```python
  pip install selenium
  ```

- **<font color="blue">下载浏览器驱动</font>**：
  - Chrome：chromedriver
  - Firefox：geckodriver
  - Edge：msedgedriver

- **<font color="green">驱动配置</font>**：
  ```python
  from selenium import webdriver
  
  # Chrome浏览器
  driver = webdriver.Chrome(executable_path='chromedriver路径')
  
  # Firefox浏览器
  driver = webdriver.Firefox(executable_path='geckodriver路径')
  
  # Edge浏览器
  driver = webdriver.Edge(executable_path='msedgedriver路径')
  ```

### 元素定位

- **<font color="red">常用定位方法</font>**：
  ```python
  # ID定位
  element = driver.find_element_by_id('id值')
  
  # 类名定位
  element = driver.find_element_by_class_name('class值')
  
  # 标签名定位
  element = driver.find_element_by_tag_name('标签名')
  
  # 链接文本定位
  element = driver.find_element_by_link_text('链接文本')
  
  # 部分链接文本定位
  element = driver.find_element_by_partial_link_text('部分链接文本')
  
  # XPath定位
  element = driver.find_element_by_xpath('//xpath表达式')
  
  # CSS选择器定位
  element = driver.find_element_by_css_selector('css选择器')
  ```

- **<font color="blue">新版API</font>**：
  ```python
  from selenium.webdriver.common.by import By
  
  # 使用By类定位元素
  element = driver.find_element(By.ID, 'id值')
  element = driver.find_element(By.CLASS_NAME, 'class值')
  element = driver.find_element(By.TAG_NAME, '标签名')
  element = driver.find_element(By.LINK_TEXT, '链接文本')
  element = driver.find_element(By.PARTIAL_LINK_TEXT, '部分链接文本')
  element = driver.find_element(By.XPATH, '//xpath表达式')
  element = driver.find_element(By.CSS_SELECTOR, 'css选择器')
  ```

### 等待机制

- **<font color="red">隐式等待</font>**：
  ```python
  # 设置隐式等待时间为10秒
  driver.implicitly_wait(10)
  ```

- **<font color="blue">显式等待</font>**：
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  
  # 等待元素可点击，最多等待10秒
  element = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.ID, '元素ID'))
  )
  ```

- **<font color="green">常用的预期条件</font>**：
  - `presence_of_element_located`：元素存在于DOM中
  - `visibility_of_element_located`：元素在页面上可见
  - `element_to_be_clickable`：元素可点击
  - `text_to_be_present_in_element`：元素包含指定文本

### 页面交互

- **<font color="red">基本操作</font>**：
  ```python
  # 打开网页
  driver.get('https://www.example.com')
  
  # 获取当前URL
  current_url = driver.current_url
  
  # 获取页面标题
  title = driver.title
  
  # 获取页面源码
  page_source = driver.page_source
  
  # 前进和后退
  driver.forward()
  driver.back()
  
  # 刷新页面
  driver.refresh()
  
  # 关闭当前窗口
  driver.close()
  
  # 关闭浏览器
  driver.quit()
  ```

- **<font color="blue">元素操作</font>**：
  ```python
  # 点击元素
  element.click()
  
  # 输入文本
  element.send_keys('要输入的文本')
  
  # 清空文本
  element.clear()
  
  # 获取元素文本
  text = element.text
  
  # 获取元素属性
  attribute = element.get_attribute('属性名')
  
  # 检查元素是否显示
  is_displayed = element.is_displayed()
  
  # 检查元素是否启用
  is_enabled = element.is_enabled()
  
  # 检查元素是否被选中
  is_selected = element.is_selected()
  ```

## 典型示例

### 自动登录示例

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初始化浏览器驱动
driver = webdriver.Chrome()

# 打开登录页面
driver.get('https://example.com/login')

# 定位用户名输入框并输入
username_input = driver.find_element(By.ID, 'username')
username_input.send_keys('your_username')

# 定位密码输入框并输入
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys('your_password')

# 定位登录按钮并点击
login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
login_button.click()

# 等待登录成功，判断是否跳转到首页
try:
    WebDriverWait(driver, 10).until(
        EC.url_contains('dashboard')
    )
    print('登录成功！')
except:
    print('登录失败！')

# 关闭浏览器
driver.quit()
```

### 处理下拉菜单

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# 初始化浏览器驱动
driver = webdriver.Chrome()

# 打开包含下拉菜单的页面
driver.get('https://example.com/dropdown')

# 定位下拉菜单元素
select_element = driver.find_element(By.ID, 'dropdown_id')

# 创建Select对象
select = Select(select_element)

# 选择选项的方法
select.select_by_index(1)  # 通过索引选择（从0开始）
select.select_by_value('option_value')  # 通过value属性选择
select.select_by_visible_text('Option Text')  # 通过可见文本选择

# 获取所有选项
all_options = select.options
for option in all_options:
    print(option.text)

# 关闭浏览器
driver.quit()
```

## 实际示例

### 爬取动态加载的商品信息

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# 初始化浏览器驱动
driver = webdriver.Chrome()
driver.maximize_window()

# 打开目标网站
driver.get('https://example.com/products')

# 创建CSV文件保存数据
with open('products.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['商品名称', '价格', '评分', '评论数'])
    
    # 滚动页面加载更多商品
    for _ in range(5):  # 滚动5次
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 等待新内容加载
        time.sleep(2)
        
        # 获取所有商品元素
        products = driver.find_elements(By.CSS_SELECTOR, '.product-item')
        
        # 提取每个商品的信息
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, '.product-name').text
                price = product.find_element(By.CSS_SELECTOR, '.product-price').text
                rating = product.find_element(By.CSS_SELECTOR, '.product-rating').text
                reviews = product.find_element(By.CSS_SELECTOR, '.product-reviews').text
                
                # 写入CSV文件
                writer.writerow([name, price, rating, reviews])
            except:
                continue

# 关闭浏览器
driver.quit()

print('商品信息爬取完成！')
```

### 自动化测试网站功能

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初始化浏览器驱动
driver = webdriver.Chrome()

# 测试结果列表
test_results = []

try:
    # 测试1：登录功能
    driver.get('https://example.com/login')
    
    # 输入用户名和密码
    driver.find_element(By.ID, 'username').send_keys('test_user')
    driver.find_element(By.ID, 'password').send_keys('test_password')
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    
    # 验证登录成功
    WebDriverWait(driver, 10).until(EC.url_contains('dashboard'))
    test_results.append(('登录功能', '通过'))
    
    # 测试2：搜索功能
    search_box = driver.find_element(By.ID, 'search')
    search_box.send_keys('测试关键词')
    search_box.submit()
    
    # 验证搜索结果
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results'))
    )
    results = driver.find_elements(By.CSS_SELECTOR, '.result-item')
    if len(results) > 0:
        test_results.append(('搜索功能', '通过'))
    else:
        test_results.append(('搜索功能', '失败'))
    
    # 测试3：退出登录
    driver.find_element(By.ID, 'logout').click()
    WebDriverWait(driver, 10).until(EC.url_contains('login'))
    test_results.append(('退出登录', '通过'))
    
except Exception as e:
    test_results.append(('发生异常', str(e)))
finally:
    # 输出测试结果
    print('测试结果汇总：')
    for test, result in test_results:
        print(f'{test}: {result}')
    
    # 关闭浏览器
    driver.quit()
```

## 思考

1. **<font color="red">Selenium与requests的区别和适用场景？</font>**
   - Selenium可以执行JavaScript，适合爬取动态加载的内容
   - Requests更轻量级，适合静态网页的爬取
   - Selenium可以模拟用户操作，适合需要交互的场景

2. **<font color="blue">如何处理网站的验证码问题？</font>**
   - 使用OCR技术识别简单验证码
   - 对于复杂验证码，可以考虑验证码识别服务
   - 某些情况下可以绕过验证码（如使用cookies）

3. **<font color="green">如何优化Selenium的执行效率？</font>**
   - 使用无头模式（headless mode）提高速度
   - 禁用图片和JavaScript加快加载
   - 合理设置等待时间，避免不必要的延迟

## 知识点

### Selenium基础

- **<font color="red">WebDriver</font>**：
  - 浏览器驱动程序，用于控制浏览器行为
  - 支持多种浏览器：Chrome、Firefox、Edge等
  - 提供统一的API接口操作不同浏览器

- **<font color="blue">元素定位</font>**：
  - ID、类名、标签名、链接文本等多种定位方式
  - XPath和CSS选择器提供更灵活的定位能力
  - 可以定位单个元素或元素集合

- **<font color="green">等待策略</font>**：
  - 隐式等待：全局设置，等待元素出现
  - 显式等待：针对特定元素，可设置条件
  - 流畅等待：自定义轮询频率和忽略异常

### 高级功能

- **<font color="red">JavaScript执行</font>**：
  ```python
  # 执行JavaScript代码
  driver.execute_script("return document.title;")
  
  # 滚动页面
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  ```

- **<font color="blue">截图功能</font>**：
  ```python
  # 截取整个页面
  driver.save_screenshot('screenshot.png')
  
  # 截取特定元素
  element.screenshot('element.png')
  ```

- **<font color="green">多窗口处理</font>**：
  ```python
  # 获取当前窗口句柄
  current_window = driver.current_window_handle
  
  # 获取所有窗口句柄
  all_windows = driver.window_handles
  
  # 切换到新窗口
  driver.switch_to.window(all_windows[-1])
  ```

- **<font color="purple">iframe处理</font>**：
  ```python
  # 通过索引切换
  driver.switch_to.frame(0)
  
  # 通过ID或名称切换
  driver.switch_to.frame('iframe_id')
  
  # 通过元素对象切换
  iframe = driver.find_element(By.ID, 'iframe_id')
  driver.switch_to.frame(iframe)
  
  # 切回主文档
  driver.switch_to.default_content()
  ```

## 小结

- **<font color="red">Selenium是一个强大的浏览器自动化工具，可以模拟用户操作</font>**
- **<font color="blue">通过各种定位方法可以精确找到页面元素并进行操作</font>**
- **<font color="green">等待机制确保元素在操作前已经加载完成</font>**
- **<font color="purple">可以处理JavaScript动态加载的内容，适合复杂网页的爬取</font>**
- **<font color="orange">支持多窗口、iframe、弹窗等复杂页面结构的处理</font>**

## 总结

Selenium自动化是爬虫开发中的重要工具，特别适合处理动态加载内容和需要交互的网站。通过本节学习，我们掌握了Selenium的基本原理、安装配置、元素定位、等待机制和页面交互等核心知识点。

在实际应用中，Selenium可以帮助我们实现网站自动化测试、数据采集、表单自动填写等功能。通过合理使用显式等待和隐式等待，可以有效处理网页加载延迟的问题。同时，Selenium还提供了丰富的API用于处理复杂的页面结构，如多窗口、iframe等。

需要注意的是，Selenium相比requests等库运行效率较低，因此在实际项目中应根据需求选择合适的工具。对于简单的静态网页，requests可能是更好的选择；而对于复杂的动态网页，Selenium则是不可或缺的工具。