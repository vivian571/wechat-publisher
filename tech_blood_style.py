"""
热血技术风格CSS样式 - 专为编程技术文章设计
"""

# 热血技术风格CSS样式定义
TECH_STYLE_CSS = """
/* 热血技术风格 - 深色主题 */
.tech-blood-style {
    background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
    color: #e0e0e0;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    line-height: 1.6;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(255, 68, 68, 0.1);
    border: 1px solid #333;
}

/* 标题样式 - 热血红 */
.tech-blood-style h1, .tech-blood-style h2, .tech-blood-style h3 {
    color: #ff4444;
    text-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
    border-left: 4px solid #ff4444;
    padding-left: 15px;
    margin: 20px 0 15px 0;
    font-weight: 700;
}

.tech-blood-style h1 {
    font-size: 2.2em;
    background: linear-gradient(90deg, #ff4444, #ff8888);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border-left: none;
    text-align: center;
    padding: 10px;
    border-bottom: 2px solid #ff4444;
}

.tech-blood-style h2 {
    font-size: 1.8em;
    background: rgba(255, 68, 68, 0.1);
    padding: 8px 15px;
    border-radius: 4px;
}

.tech-blood-style h3 {
    font-size: 1.4em;
    color: #ff6666;
}

/* 段落样式 */
.tech-blood-style p {
    margin: 15px 0;
    color: #d0d0d0;
    font-size: 16px;
}

/* 代码块样式 - 黑客风格 */
.tech-blood-style pre {
    background: #1e1e1e;
    border: 1px solid #ff4444;
    border-radius: 6px;
    padding: 15px;
    overflow-x: auto;
    box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
    margin: 20px 0;
}

.tech-blood-style code {
    background: #2a2a2a;
    color: #ffcc00;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 14px;
    border: 1px solid #444;
}

.tech-blood-style pre code {
    background: none;
    color: #ffcc00;
    border: none;
    padding: 0;
}

/* 行内代码特殊颜色 */
.tech-blood-style code.language-bash {
    color: #00ff88;
}

.tech-blood-style code.language-python {
    color: #ff8800;
}

/* 引用样式 */
.tech-blood-style blockquote {
    border-left: 4px solid #ff4444;
    background: rgba(255, 68, 68, 0.05);
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #ffaaaa;
}

/* 列表样式 */
.tech-blood-style ul, .tech-blood-style ol {
    margin: 15px 0;
    padding-left: 30px;
}

.tech-blood-style li {
    margin: 8px 0;
    color: #e0e0e0;
}

.tech-blood-style li::marker {
    color: #ff4444;
}

/* 链接样式 */
.tech-blood-style a {
    color: #ff8844;
    text-decoration: none;
    border-bottom: 1px solid #ff8844;
    transition: all 0.3s ease;
}

.tech-blood-style a:hover {
    color: #ffaa66;
    border-bottom: 1px solid #ffaa66;
    text-shadow: 0 0 5px rgba(255, 136, 68, 0.5);
}

/* 强调文本 */
.tech-blood-style strong {
    color: #ff6666;
    font-weight: 700;
    text-shadow: 0 0 3px rgba(255, 102, 102, 0.3);
}

.tech-blood-style em {
    color: #ffaa88;
    font-style: italic;
}

/* 表格样式 */
.tech-blood-style table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    overflow: hidden;
}

.tech-blood-style th {
    background: linear-gradient(135deg, #ff4444, #cc3333);
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

.tech-blood-style td {
    padding: 10px 12px;
    border-bottom: 1px solid #333;
    color: #d0d0d0;
}

.tech-blood-style tr:nth-child(even) {
    background: rgba(255, 68, 68, 0.05);
}

/* 分割线 */
.tech-blood-style hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff4444, transparent);
    margin: 30px 0;
}

/* 标签样式 */
.tech-tag {
    display: inline-block;
    background: linear-gradient(135deg, #ff4444, #cc3333);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    margin: 0 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.tech-tag.opensource {
    background: linear-gradient(135deg, #00ff88, #00cc66);
}

.tech-tag.monitor {
    background: linear-gradient(135deg, #ffaa00, #ff8800);
}

/* 标题前缀装饰 */
.tech-blood-style h2::before {
    content: "▶ ";
    color: #ff4444;
    font-weight: bold;
}

.tech-blood-style h3::before {
    content: "⚡ ";
    color: #ff6666;
}

/* 代码块行号 */
.tech-blood-style pre {
    counter-reset: line;
}

.tech-blood-style pre code {
    counter-increment: line;
}

.tech-blood-style pre code::before {
    content: counter(line);
    position: absolute;
    left: 0;
    width: 30px;
    text-align: right;
    color: #666;
    border-right: 1px solid #444;
    padding-right: 10px;
    margin-right: 15px;
}
"""

# 热血技术风格HTML模板
TECH_BLOOD_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css_style}
        
        /* 额外的热血动画效果 */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .pulse-effect {
            animation: pulse 2s infinite;
        }
        
        /* 标题发光效果 */
        .glow-title {
            text-shadow: 0 0 10px #ff4444, 0 0 20px #ff4444, 0 0 30px #ff4444;
        }
    </style>
</head>
<body>
    <div class="tech-blood-style">
        {content}
    </div>
</body>
</html>
"""

def get_tech_blood_style():
    """获取热血技术风格CSS样式"""
    return TECH_STYLE_CSS

def get_tech_blood_html_template():
    """获取热血技术风格HTML模板"""
    return TECH_BLOOD_HTML_TEMPLATE

# 示例热血风格Markdown内容
TECH_BLOOD_SAMPLE_MARKDOWN = """# 🔥 别再为监控付费了！开源神器 Uptime Kuma 火了

**标签**：<span class="tech-tag opensource">开源</span> <span class="tech-tag monitor">监控</span> | **发布于**：2025年07月22日

---

## ⚡ 什么是 Uptime Kuma？

> **Uptime Kuma** 是一个开源的、自托管的监控工具，支持 **HTTP/HTTPS**、**TCP**、**Ping**、**DNS** 等多种监控方式。

### 🚀 核心特性

- **完全免费**：零成本，告别昂贵的商业监控服务
- **自托管**：数据完全掌控在自己手中
- **多协议支持**：HTTP、TCP、Ping、DNS 全覆盖
- **实时通知**：支持邮件、Webhook、Telegram 等
- **美观仪表板**：现代化的 Web 界面

## 💻 快速安装

```bash
# 使用 Docker 一键安装
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

## 🔧 配置监控

1. **访问界面**：打开 `http://your-server:3001`
2. **添加监控**：点击 "Add New Monitor"
3. **选择类型**：HTTP/HTTPS、TCP、Ping 等
4. **设置参数**：URL、检查频率、超时时间

### 📊 监控效果

| 监控类型 | 响应时间 | 可用性 | 状态 |
|---------|---------|--------|------|
| 网站A | 120ms | 99.9% | ✅ |
| API服务 | 85ms | 99.5% | ✅ |
| 数据库 | 45ms | 98.2% | ⚠️ |

> **💡 小贴士**：建议设置 **1分钟** 的检查频率，既能及时发现问题，又不会给服务器造成太大压力。

## 🎯 为什么选择 Uptime Kuma？

**传统商业监控** vs **Uptime Kuma**：

- 💰 **成本**：月费 $20+ → **完全免费**
- 🔒 **数据**：第三方托管 → **自托管掌控**
- ⚙️ **灵活性**：功能固定 → **开源可定制**
- 📈 **扩展性**：受限于套餐 → **无限制**

---

## 🎉 总结

**Uptime Kuma** 不仅功能强大，而且完全免费开源。对于个人开发者、初创公司来说，绝对是监控方案的最佳选择！

> **🔥 热血推荐**：立即部署，让你的服务监控不再花冤枉钱！

**相关资源**：
- GitHub: [https://github.com/louislam/uptime-kuma](https://github.com/louislam/uptime-kuma)
- 官方文档：[https://github.com/louislam/uptime-kuma/wiki](https://github.com/louislam/uptime-kuma/wiki)
"""