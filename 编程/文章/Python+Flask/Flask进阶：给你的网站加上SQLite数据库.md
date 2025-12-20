# Flask进阶：给你的网站加上SQLite数据库

嘿，小伙伴们！上次我们一起搭建了人生中的第一个Flask网站，是不是感觉特别有成就感？

但是，一个只能看不能「**记住东西**」的网站，就像是一个没有记忆的人，用户填的表单、发的留言都是"过眼云烟"，服务器重启后全都不见了！

今天，我就要带你给网站装上"**记忆力**"——**SQLite数据库**，让你的Flask网站能够持久化存储数据，变得更加强大！

## 一、SQLite是什么？为啥选它？

**SQLite**是一个超轻量级的关系型数据库，它的整个数据库就是**一个文件**，不需要安装服务器，不需要配置，简直就是懒人福音！

相比MySQL、PostgreSQL这些"大块头"数据库，SQLite就像是一个"**迷你口袋数据库**"，随身携带，拿来即用！

对于我们的Flask小网站来说，SQLite绝对是最佳搭档，因为：

1. **零配置**：不需要安装额外的数据库服务器，省去一堆麻烦事
2. **轻量级**：整个数据库就是一个文件，拷贝备份超方便
3. **性能够用**：对于中小型网站，性能完全够用
4. **Python内置支持**：Python标准库直接支持SQLite，不需要额外安装驱动

## 二、准备工作：安装必要的扩展

虽然Python内置了SQLite支持，但直接用原生SQL语句操作数据库太麻烦了，就像用汇编语言写程序一样痛苦！

我们需要一个更高级的工具——**Flask-SQLAlchemy**，它是一个超强的ORM（对象关系映射）工具，让我们可以用Python对象来操作数据库，而不是写SQL语句。

打开命令提示符，安装这个扩展：

```bash
pip install flask-sqlalchemy
```

就这么简单，一行命令搞定！

## 三、配置数据库：告诉Flask在哪里存数据

现在，我们需要修改之前的app.py文件，添加数据库配置：

```python
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 设置数据库文件路径（在项目文件夹中创建一个名为instance的文件夹，数据库文件将存储在那里）
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'messages.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 创建数据库对象
db = SQLAlchemy(app)

# 其他路由和代码...

if __name__ == '__main__':
    app.run(debug=True)
```

这段代码做了什么？它告诉Flask：

1. 我们要用SQLAlchemy来操作数据库
2. 数据库文件叫messages.db，放在项目的instance文件夹下
3. 不要跟踪数据库修改（这样可以提高性能）

## 四、创建数据模型：设计数据的"蓝图"

数据库需要知道我们要存什么数据，就像建房子前需要设计图纸一样。

在app.py中，添加一个Message模型，用来存储联系表单的留言：

```python
# 定义数据模型
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键，自动递增
    name = db.Column(db.String(100), nullable=False)  # 姓名，不能为空
    email = db.Column(db.String(100), nullable=False)  # 邮箱，不能为空
    message = db.Column(db.Text, nullable=False)  # 留言内容，不能为空
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间，默认为当前时间
    
    def __repr__(self):
        return f'<Message from {self.name}: {self.message[:20]}...>'
```

这个模型定义了留言的结构：每条留言都有ID、姓名、邮箱、内容和创建时间。

**db.Column**告诉SQLAlchemy这是一个数据库列，括号里的参数定义了列的类型和约束。

**__repr__**方法定义了在打印这个对象时显示的内容，方便我们调试。

## 五、创建数据库表：把"蓝图"变成实体

模型只是定义了数据结构，我们还需要在数据库中创建实际的表。

在app.py的最后，添加以下代码：

```python
if __name__ == '__main__':
    # 创建数据库表（如果不存在）
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

这段代码会在应用启动时检查数据库表是否存在，如果不存在就创建它。

## 六、保存表单数据：把留言存进数据库

现在，我们修改contact函数，让它把表单数据保存到数据库中：

```python
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # 从表单获取数据
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']
        
        # 创建新的Message对象
        new_message = Message(name=name, email=email, message=message_text)
        
        # 添加到数据库会话
        db.session.add(new_message)
        
        # 提交会话，保存到数据库
        db.session.commit()
        
        # 重定向到感谢页面
        return render_template('thanks.html', name=name)
    
    # GET请求，显示表单
    return render_template('contact.html')
```

这段代码做了什么？

1. 从表单获取用户输入的姓名、邮箱和留言
2. 创建一个新的Message对象
3. 把这个对象添加到数据库会话
4. 提交会话，把数据保存到数据库
5. 重定向到感谢页面

就这么简单，用户的留言就永久保存下来了！

## 七、显示留言列表：把数据库中的数据展示出来

存储数据只是第一步，我们还需要把数据展示出来，让用户看到所有的留言。

首先，添加一个新的路由：

```python
@app.route('/messages')
def messages():
    # 从数据库获取所有留言，按创建时间倒序排列
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    
    # 渲染模板，传入留言列表
    return render_template('messages.html', messages=all_messages)
```

然后，创建一个新的模板文件messages.html：

```html
<!DOCTYPE html>
<html>
<head>
    <title>留言列表</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <style>
        .message {
            background-color: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message-info {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .message-content {
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <h1>留言列表</h1>
    <nav>
        <a href="/">首页</a>
        <a href="/about">关于</a>
        <a href="/contact">联系我</a>
        <a href="/messages">留言列表</a>
    </nav>
    
    {% if messages %}
        {% for message in messages %}
            <div class="message">
                <div class="message-info">
                    <strong>{{ message.name }}</strong> ({{ message.email }})
                    <span>{{ message.created_at.strftime('%Y-%m-%d %H:%M') }}</span>
                </div>
                <div class="message-content">
                    {{ message.message }}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>暂时没有留言，快来留下第一条吧！</p>
    {% endif %}
    
    <p><a href="/contact">我也要留言</a></p>
</body>
</html>
```

最后，别忘了在导航栏中添加一个链接到留言列表页面。

在home.html、about.html和contact.html的导航栏中添加：

```html
<a href="/messages">留言列表</a>
```

现在，用户可以查看所有人的留言了，是不是很酷？

## 八、进阶操作：CRUD全家桶

在数据库操作中，有一个著名的概念叫**CRUD**，代表四种基本操作：

- **C**reate（创建）：我们已经实现了，就是保存新留言
- **R**ead（读取）：我们也实现了，就是显示留言列表
- **U**pdate（更新）：修改已有的留言
- **D**elete（删除）：删除不需要的留言

如果你想实现完整的CRUD功能，可以添加编辑和删除留言的功能。

这里简单展示一下删除留言的实现：

```python
@app.route('/delete/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    # 查找指定ID的留言
    message = Message.query.get_or_404(message_id)
    
    # 从数据库中删除
    db.session.delete(message)
    db.session.commit()
    
    # 重定向到留言列表
    return redirect(url_for('messages'))
```

然后在messages.html的每条留言下添加一个删除按钮：

```html
<form method="POST" action="/delete/{{ message.id }}" style="display: inline;">
    <button type="submit" onclick="return confirm('确定要删除这条留言吗？');">删除</button>
</form>
```

这样，管理员就可以删除不适当的留言了！

## 九、数据库迁移：安全升级数据库结构

随着网站功能的增加，你可能需要修改数据库结构，比如添加新的字段。

但是，直接修改模型会导致数据丢失！怎么办？

这时候就需要用到**Flask-Migrate**扩展，它可以安全地升级数据库结构，同时保留现有数据。

安装Flask-Migrate：

```bash
pip install flask-migrate
```

然后在app.py中添加配置：

```python
from flask_migrate import Migrate

# 初始化迁移对象
migrate = Migrate(app, db)
```

现在，你可以使用命令行工具来管理数据库迁移：

```bash
flask db init    # 初始化迁移仓库
flask db migrate -m "Initial migration."  # 创建迁移脚本
flask db upgrade  # 应用迁移
```

这样，你就可以安全地修改数据库结构，而不用担心数据丢失了！

## 总结：你的网站现在有了"记忆力"！

恭喜你！通过这篇教程，你已经成功地给Flask网站添加了SQLite数据库，实现了数据的持久化存储！

我们学习了：

1. SQLite数据库的基本概念
2. 使用Flask-SQLAlchemy进行ORM操作
3. 创建数据模型和数据库表
4. 实现CRUD操作（创建、读取、更新、删除）
5. 使用Flask-Migrate进行数据库迁移

有了数据库，你的网站就像有了记忆一样，可以记住用户的信息和操作，这为实现更复杂的功能打下了基础。

下期预告：我们将探索如何实现**用户认证系统**，让你的网站支持用户注册、登录和权限控制，敬请期待！

你有什么关于Flask和数据库的问题？欢迎在评论区留言，我们一起讨论！