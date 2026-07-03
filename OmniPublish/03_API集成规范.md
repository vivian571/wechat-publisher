# OmniPublish - API 集成规范文档

> **版本**: v1.0  
> **更新日期**: 2026-01-01

---

## 📋 目录

1. [国际平台 API](#国际平台-api)
2. [国内平台 API](#国内平台-api)
3. [通用规范](#通用规范)
4. [错误处理](#错误处理)
5. [速率限制](#速率限制)

---

## 国际平台 API

### 1. Dev.to API

**官方文档**: https://developers.forem.com/api/v1

#### 认证方式
```http
GET /api/articles
Host: dev.to
api-key: YOUR_API_KEY
```

#### 创建文章
```http
POST /api/articles
Content-Type: application/json

{
  "article": {
    "title": "文章标题",
    "body_markdown": "Markdown 内容",
    "published": true,
    "tags": ["javascript", "tutorial"],
    "series": "系列名称",
    "canonical_url": "https://myblog.com/article",
    "description": "文章摘要",
    "organization_id": 12345
  }
}
```

**响应示例**:
```json
{
  "id": 123456,
  "title": "文章标题",
  "url": "https://dev.to/username/article-slug",
  "canonical_url": "https://myblog.com/article",
  "published_at": "2026-01-01T00:00:00Z",
  "tags": ["javascript", "tutorial"]
}
```

#### 更新文章
```http
PUT /api/articles/{id}
Content-Type: application/json

{
  "article": {
    "title": "更新后的标题",
    "body_markdown": "更新后的内容"
  }
}
```

#### 注意事项
- ✅ 最多支持 **4 个标签**
- ✅ 标签名必须已存在于 Dev.to 平台
- ✅ 支持 Markdown 所有语法
- ⚠️ 图片必须使用公共 URL (不支持本地路径)

---

### 2. Hashnode API

**官方文档**: https://apidocs.hashnode.com/

#### 认证方式
```http
POST https://api.hashnode.com
Authorization: YOUR_ACCESS_TOKEN
Content-Type: application/json
```

#### 创建文章 (GraphQL)
```graphql
mutation CreateStory {
  createPublicationStory(
    publicationId: "YOUR_PUBLICATION_ID"
    input: {
      title: "文章标题"
      contentMarkdown: "Markdown 内容"
      tags: [
        { _id: "tag_id_1", name: "JavaScript" }
        { _id: "tag_id_2", name: "Tutorial" }
      ]
      coverImageURL: "https://example.com/cover.jpg"
      isPartOfPublication: {
        publicationId: "YOUR_PUBLICATION_ID"
      }
      sourcedFromGithub: false
    }
  ) {
    post {
      _id
      slug
      title
      url
    }
  }
}
```

**Python 实现**:
```python
import httpx

def publish_to_hashnode(token: str, pub_id: str, metadata, content):
    query = """
    mutation CreateStory($input: CreateStoryInput!) {
      createPublicationStory(
        publicationId: "%s"
        input: $input
      ) {
        post {
          _id
          slug
          url
        }
      }
    }
    """ % pub_id
    
    variables = {
        "input": {
            "title": metadata.title,
            "contentMarkdown": content,
            "tags": [{"name": tag} for tag in metadata.tags],
            "coverImageURL": metadata.cover_image
        }
    }
    
    response = httpx.post(
        "https://api.hashnode.com",
        headers={"Authorization": token},
        json={"query": query, "variables": variables}
    )
    
    return response.json()
```

#### 注意事项
- ✅ 使用 GraphQL,需构造 Mutation
- ✅ 标签可以动态创建
- ⚠️ 需要先创建 Publication (个人博客)
- ⚠️ `publicationId` 可在个人设置中获取

---

### 3. Medium API

**官方文档**: https://github.com/Medium/medium-api-docs

#### 认证方式
```http
GET /v1/me
Host: api.medium.com
Authorization: Bearer YOUR_INTEGRATION_TOKEN
```

#### 获取用户 ID
```http
GET /v1/me

Response:
{
  "data": {
    "id": "user_id_here",
    "username": "username",
    "name": "Full Name"
  }
}
```

#### 创建文章
```http
POST /v1/users/{userId}/posts
Content-Type: application/json

{
  "title": "文章标题",
  "contentFormat": "markdown",
  "content": "Markdown 内容",
  "tags": ["javascript", "tutorial"],
  "canonicalUrl": "https://myblog.com/article",
  "publishStatus": "draft",
  "license": "all-rights-reserved",
  "notifyFollowers": false
}
```

**响应示例**:
```json
{
  "data": {
    "id": "post_id",
    "title": "文章标题",
    "url": "https://medium.com/@username/article-slug",
    "canonicalUrl": "https://myblog.com/article",
    "publishStatus": "draft",
    "publishedAt": null
  }
}
```

#### 注意事项
- ⚠️ **只能创建草稿或 Unlisted 文章**
- ⚠️ **不支持更新已发布文章**
- ✅ 最多支持 **5 个标签**
- ✅ `publishStatus` 可选值: `"public"`, `"draft"`, `"unlisted"`
- 💡 建议设置为 `"draft"`,人工审核后再发布

---

### 4. Ghost API

**官方文档**: https://ghost.org/docs/admin-api/

#### 认证方式 (JWT)
```python
import jwt
import datetime

def generate_ghost_token(admin_api_key: str) -> str:
    """生成 Ghost Admin API Token"""
    
    # API Key 格式: id:secret
    key_id, secret = admin_api_key.split(':')
    
    # 生成 JWT
    payload = {
        'iat': int(datetime.datetime.now().timestamp()),
        'exp': int((datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp()),
        'aud': '/admin/'
    }
    
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers={'kid': key_id})
    
    return token
```

#### 创建文章
```http
POST /ghost/api/admin/posts/
Authorization: Ghost {JWT_TOKEN}
Content-Type: application/json

{
  "posts": [{
    "title": "文章标题",
    "markdown": "Markdown 内容",
    "status": "published",
    "tags": [
      {"name": "JavaScript"},
      {"name": "Tutorial"}
    ],
    "feature_image": "https://example.com/cover.jpg",
    "canonical_url": "https://myblog.com/article"
  }]
}
```

#### 注意事项
- ✅ 支持完整的 Markdown 语法
- ✅ 可直接发布 (`status: "published"`) 或保存为草稿 (`status: "draft"`)
- ⚠️ 需要自托管 Ghost 实例
- ⚠️ JWT Token 有效期仅 5 分钟,需动态生成

---

## 国内平台 API

### 1. 稀土掘金 (私有 API)

> [!WARNING]
> 掘金没有官方 API,以下为逆向工程结果,可能随时失效

#### 认证方式
```http
POST https://api.juejin.cn/content_api/v1/article/publish
Cookie: sessionid=xxx; sessionid_ss=xxx
x-secsdk-csrf-token: {从 Cookie 中提取}
Content-Type: application/json
```

#### 提取 CSRF Token
```python
def extract_csrf_token(cookie: str) -> str:
    """从 Cookie 中提取 CSRF Token"""
    import re
    
    match = re.search(r'sessionid=([^;]+)', cookie)
    if match:
        return match.group(1)[:32]  # 取前 32 位
    
    raise ValueError("无法提取 CSRF Token")
```

#### 创建草稿
```http
POST /content_api/v1/article_draft/create
Content-Type: application/json

{
  "title": "文章标题",
  "content": "Markdown 内容",
  "mark_content": "Markdown 内容",
  "tag_ids": ["tag_id_1", "tag_id_2"],
  "category_id": "category_id",
  "cover_image": "https://example.com/cover.jpg",
  "brief_content": "文章摘要"
}
```

**响应**:
```json
{
  "err_no": 0,
  "err_msg": "success",
  "data": {
    "draft_id": "draft_id_here"
  }
}
```

#### 发布草稿
```http
POST /content_api/v1/article/publish
Content-Type: application/json

{
  "draft_id": "draft_id_here",
  "sync_to_org": false,
  "column_ids": []
}
```

#### 分类 ID 映射
```python
JUEJIN_CATEGORIES = {
    "后端": "6809637767543259144",
    "前端": "6809637767543259149",
    "Android": "6809637767543259150",
    "iOS": "6809637767543259151",
    "人工智能": "6809637773935378440",
    "开发工具": "6809637773935378439",
    "代码人生": "6809637776263217160",
    "阅读": "6809637772874219534"
}
```

#### 注意事项
- ⚠️ **必须先创建草稿,再发布**
- ⚠️ **Cookie 有效期约 30 天,需定期更新**
- ⚠️ **需要添加随机延时 (2-5 秒)**
- ⚠️ **标签 ID 需要预先查询**

---

### 2. 微信公众号 (官方 API)

**官方文档**: https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html

#### 获取 Access Token
```http
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET

Response:
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

**Python 实现**:
```python
import httpx
import time

class WeChatTokenManager:
    """微信 Access Token 管理器"""
    
    def __init__(self, appid: str, secret: str):
        self.appid = appid
        self.secret = secret
        self.token = None
        self.expires_at = 0
    
    def get_token(self) -> str:
        """获取有效的 Access Token"""
        
        # 检查是否过期
        if self.token and time.time() < self.expires_at:
            return self.token
        
        # 刷新 Token
        response = httpx.get(
            "https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.appid,
                "secret": self.secret
            }
        )
        
        data = response.json()
        self.token = data['access_token']
        self.expires_at = time.time() + data['expires_in'] - 300  # 提前 5 分钟刷新
        
        return self.token
```

#### 上传图片素材
```http
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=image
Content-Type: multipart/form-data

media: (binary image data)
```

**Python 实现**:
```python
def upload_image_to_wechat(access_token: str, image_path: str) -> str:
    """上传图片到微信素材库"""
    
    with open(image_path, 'rb') as f:
        files = {'media': ('image.jpg', f, 'image/jpeg')}
        
        response = httpx.post(
            f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image",
            files=files
        )
    
    data = response.json()
    return data['media_id']
```

#### 创建草稿
```http
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN
Content-Type: application/json

{
  "articles": [{
    "title": "文章标题",
    "author": "作者名",
    "digest": "文章摘要",
    "content": "HTML 内容 (不支持 Markdown)",
    "content_source_url": "https://myblog.com/article",
    "thumb_media_id": "封面图 media_id",
    "need_open_comment": 1,
    "only_fans_can_comment": 0
  }]
}
```

**响应**:
```json
{
  "media_id": "draft_media_id",
  "errcode": 0,
  "errmsg": "ok"
}
```

#### Markdown 转微信 HTML
```python
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup

def markdown_to_wechat_html(markdown: str) -> str:
    """转换 Markdown 为微信富文本"""
    
    # 1. Markdown 转 HTML
    md = MarkdownIt()
    html = md.render(markdown)
    
    # 2. 应用微信样式
    soup = BeautifulSoup(html, 'html.parser')
    
    # 标题样式
    for h1 in soup.find_all('h1'):
        h1['style'] = 'font-size: 22px; font-weight: bold; margin: 20px 0; color: #333;'
    
    for h2 in soup.find_all('h2'):
        h2['style'] = 'font-size: 18px; font-weight: bold; margin: 16px 0; color: #333; border-left: 4px solid #3eaf7c; padding-left: 10px;'
    
    # 代码块样式
    for pre in soup.find_all('pre'):
        pre['style'] = 'background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto;'
    
    for code in soup.find_all('code'):
        if code.parent.name != 'pre':
            code['style'] = 'background: #f0f0f0; padding: 2px 6px; border-radius: 3px; color: #e83e8c;'
    
    # 引用样式
    for blockquote in soup.find_all('blockquote'):
        blockquote['style'] = 'border-left: 4px solid #dfe2e5; padding-left: 16px; color: #6a737d; margin: 16px 0;'
    
    return str(soup)
```

#### 注意事项
- ⚠️ **不支持 Markdown,必须转换为 HTML**
- ⚠️ **图片必须上传到微信素材库,不能使用外链**
- ⚠️ **仅创建草稿,不自动群发**
- ✅ Access Token 有效期 2 小时,需缓存
- ✅ 支持多图文 (一次最多 8 篇)

---

### 3. CSDN (浏览器自动化)

> [!CAUTION]
> CSDN 没有官方 API,必须使用 Playwright 模拟浏览器操作

#### 实现方案
```python
from playwright.sync_api import sync_playwright
import time
import random

class CSDNAdapter:
    
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def publish(self, metadata, content):
        """发布文章到 CSDN"""
        
        with sync_playwright() as p:
            # 1. 启动浏览器
            browser = p.chromium.launch(
                headless=False,  # 调试时设为 False
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 2. 注入 Cookie
            context.add_cookies(self._parse_cookie(self.cookie))
            
            # 3. 打开编辑器
            page = context.new_page()
            page.goto('https://editor.csdn.net/md/')
            
            # 4. 等待编辑器加载
            page.wait_for_selector('.editor-container', timeout=10000)
            time.sleep(random.uniform(1, 2))
            
            # 5. 填充标题
            page.fill('input[placeholder*="标题"]', metadata.title)
            time.sleep(random.uniform(0.5, 1))
            
            # 6. 填充内容 (直接操作 CodeMirror)
            page.evaluate(f'''
                const editor = document.querySelector('.CodeMirror').CodeMirror;
                editor.setValue(`{content.replace('`', '\\`')}`);
            ''')
            time.sleep(random.uniform(1, 2))
            
            # 7. 选择分类
            page.click('text=选择分类')
            time.sleep(0.5)
            page.click(f'text={self._map_category(metadata.tags[0])}')
            
            # 8. 添加标签
            for tag in metadata.tags[:3]:  # CSDN 最多 3 个标签
                page.fill('input[placeholder*="标签"]', tag)
                time.sleep(0.3)
                page.keyboard.press('Enter')
            
            # 9. 点击发布
            page.click('button:has-text("发布文章")')
            
            # 10. 等待发布成功
            page.wait_for_selector('.success-tips', timeout=15000)
            
            # 11. 获取文章 URL
            article_url = page.url
            
            browser.close()
            
            return article_url
    
    def _parse_cookie(self, cookie_str: str) -> list:
        """解析 Cookie 字符串为 Playwright 格式"""
        cookies = []
        for item in cookie_str.split('; '):
            if '=' in item:
                name, value = item.split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.csdn.net',
                    'path': '/'
                })
        return cookies
    
    def _map_category(self, tag: str) -> str:
        """映射标签到 CSDN 分类"""
        mapping = {
            'python': 'Python',
            'javascript': 'Web开发',
            'java': 'Java',
            'ai': '人工智能'
        }
        return mapping.get(tag.lower(), '其他')
```

#### 注意事项
- ⚠️ **必须使用真实浏览器环境**
- ⚠️ **添加随机延时,模拟人类操作**
- ⚠️ **Cookie 有效期约 7 天,需定期更新**
- ⚠️ **成功率受网络和页面加载速度影响**
- 💡 建议设置 `headless=False` 进行调试

---

## 通用规范

### 1. 请求头标准化
```python
COMMON_HEADERS = {
    'User-Agent': 'OmniPublish/1.0 (https://github.com/yourname/omnipublish)',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
```

### 2. 超时设置
```python
import httpx

# 所有 HTTP 请求统一超时设置
client = httpx.Client(timeout=30.0)
```

### 3. 重试机制
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_request(url, **kwargs):
    response = httpx.post(url, **kwargs)
    response.raise_for_status()
    return response.json()
```

---

## 错误处理

### 标准错误响应
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIError:
    """API 错误标准结构"""
    platform: str
    error_code: Optional[str]
    error_message: str
    http_status: Optional[int]
    raw_response: dict
```

### 常见错误码

| 平台 | 错误码 | 含义 | 处理方案 |
|------|--------|------|---------|
| Dev.to | 401 | API Key 无效 | 检查环境变量 |
| Dev.to | 422 | 参数验证失败 | 检查标签数量/格式 |
| Hashnode | UNAUTHENTICATED | Token 无效 | 重新生成 Token |
| Medium | 401 | Token 过期 | 刷新 Integration Token |
| 掘金 | 403 | Cookie 过期 | 提示用户更新 Cookie |
| 微信 | 40001 | Access Token 过期 | 自动刷新 Token |

---

## 速率限制

| 平台 | 限制 | 建议策略 |
|------|------|---------|
| **Dev.to** | 无明确限制 | 每分钟不超过 10 次请求 |
| **Hashnode** | 无明确限制 | 每分钟不超过 5 次请求 |
| **Medium** | 无明确限制 | 每小时不超过 20 篇文章 |
| **掘金** | 未知 (风控严格) | 每篇文章间隔 2-5 秒 |
| **微信** | 每日 5000 次 | 缓存 Access Token |
| **CSDN** | 未知 (风控严格) | 每篇文章间隔 5-10 秒 |

**实现示例**:
```python
import time
from functools import wraps

def rate_limit(min_interval: float):
    """速率限制装饰器"""
    last_call = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            
            return result
        return wrapper
    return decorator

# 使用示例
@rate_limit(min_interval=3.0)  # 最少间隔 3 秒
def publish_to_juejin(metadata, content):
    # 发布逻辑...
    pass
```

---

## 总结

本文档提供了 OmniPublish 支持的所有平台的 API 集成规范:

✅ **国际平台**: Dev.to, Hashnode, Medium, Ghost (官方 API)  
✅ **国内平台**: 掘金 (私有 API), 微信公众号 (官方 API), CSDN (浏览器自动化)  
✅ **通用规范**: 请求头、超时、重试、错误处理、速率限制

**下一步**: 查看 [部署运维文档](./04_部署运维文档.md) 了解如何部署系统
