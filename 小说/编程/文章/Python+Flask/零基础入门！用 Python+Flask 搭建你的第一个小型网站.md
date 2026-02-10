# 零基础入门！用 Python+Flask 搭建你的第一个小型网站

嘿，小伙伴们！是不是一直想拥有自己的网站，却被那些复杂的代码和术语吓退了？

别担心！今天我就要带你用 **Python+Flask** 这对黄金搭档，轻松搞定你的第一个小型网站！

就算你是个彻彻底底的编程小白，也能跟着这篇教程，一步步搭建出一个属于自己的网站，然后得意洋洋地向朋友们炫耀："看，这是我自己做的！"

## 一、Flask 是什么？为啥选它？

**Flask** 是 Python 世界中最受欢迎的轻量级 Web 框架之一，它就像是一个「**迷你版的乐高积木套装**」，简单却能搭建出令人惊叹的作品！

相比其他框架，Flask 的学习曲线超级平缓，代码简洁到让人感动，非常适合初学者入门。

它遵循「**微框架**」的理念，核心功能精简，但可以通过扩展来增加各种功能，就像你可以根据需要往乐高基础上添加不同的积木一样灵活。

最重要的是，用 Flask 写一个能跑起来的网站只需要短短几行代码，这种即时的成就感会让你爱上编程！

## 二、准备工作：搭建开发环境

在开始编码前，我们需要准备好「**开发环境**」，就像做饭前要准备好锅碗瓢盆一样。

首先，确保你的电脑上已经安装了 **Python**（建议 3.6 版本以上），没有的话去官网下载安装包，跟着提示点下一步就行了，超简单！

接下来，我们需要安装 Flask 框架，打开命令提示符（Windows 按 Win+R，输入 cmd 回车），输入以下命令：

```bash
pip install flask
```

看到一堆文字刷屏后出现 "Successfully installed" 就说明安装成功了，是不是很简单？

为了让代码更有条理，我们创建一个项目文件夹，比如叫 "my_website"，所有代码都会放在这个文件夹里。

## 三、Hello World：第一个 Flask 应用

好了，环境准备完毕，现在我们来写人生中的第一个 Flask 应用！

在项目文件夹中创建一个名为 "app.py" 的文件，然后输入以下代码：

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello, World!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
```

就这么几行代码，一个网站的雏形就完成了，是不是超级简单？

现在，回到命令提示符，进入你的项目文件夹，运行这个文件：

```bash
python app.py
```

你会看到类似 "Running on http://127.0.0.1:5000/" 的信息，这说明你的网站已经在本地运行起来了！

打开浏览器，输入 "http://127.0.0.1:5000"，哇！你会看到一个大大的 "Hello, World!" 显示在页面上，恭喜你，你的第一个网站诞生了！

## 四、添加更多页面：让网站丰富起来

一个只有首页的网站太单调了，我们来添加更多页面，让它变得丰富起来。

修改 app.py 文件，添加更多的路由和页面：

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
```

等等，这里的 `render_template` 是什么？它是 Flask 中用来渲染 HTML 模板的函数，可以让我们的页面更加美观和动态。

在项目文件夹中创建一个名为 "templates" 的文件夹，然后在里面创建三个 HTML 文件：home.html、about.html 和 contact.html。

这里是 home.html 的简单示例：

```html
<!DOCTYPE html>
<html>
<head>
    <title>我的第一个网站</title>
</head>
<body>
    <h1>欢迎来到我的网站！</h1>
    <nav>
        <a href="/">首页</a>
        <a href="/about">关于</a>
        <a href="/contact">联系我</a>
    </nav>
    <p>这是我用 Flask 搭建的第一个网站，是不是很酷？</p>
</body>
</html>
```

类似地，你可以为 about.html 和 contact.html 创建内容，只需修改标题和正文部分。

重新运行你的应用，现在你可以通过导航栏在不同页面之间切换了，是不是感觉像模像样了？

## 五、添加样式：让网站变得好看

一个没有样式的网站就像一个没化妆的素颜，虽然本质不变，但缺少了那份惊艳。

在项目文件夹中创建一个名为 "static" 的文件夹，然后在里面创建一个 "style.css" 文件：

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

nav {
    background-color: #333;
    padding: 10px;
    margin-bottom: 20px;
}

nav a {
    color: white;
    margin-right: 15px;
    text-decoration: none;
}

h1 {
    color: #2c3e50;
}
```

然后，在 HTML 文件的 `<head>` 部分添加链接到这个 CSS 文件：

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

刷新页面，哇！你的网站立刻变得专业多了，颜色、字体、间距都变得赏心悦目。

## 六、添加交互功能：表单处理

静态页面虽好，但缺少互动就像一个只能看不能摸的展览，少了点乐趣。

让我们在 contact.html 中添加一个联系表单：

```html
<form method="POST" action="/contact">
    <div>
        <label>姓名：</label>
        <input type="text" name="name" required>
    </div>
    <div>
        <label>邮箱：</label>
        <input type="email" name="email" required>
    </div>
    <div>
        <label>留言：</label>
        <textarea name="message" required></textarea>
    </div>
    <button type="submit">发送</button>
</form>
```

然后修改 app.py 中的 contact 函数，使其能处理表单提交：

```python
from flask import Flask, render_template, request, flash, redirect

# ... 其他代码 ...

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # 在实际应用中，这里可以保存到数据库或发送邮件
        print(f"收到来自 {name}({email}) 的留言: {message}")
        return render_template('thanks.html', name=name)
    return render_template('contact.html')
```

别忘了创建一个 thanks.html 模板，用于表单提交后的感谢页面：

```html
<!DOCTYPE html>
<html>
<head>
    <title>感谢您的留言</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>谢谢你，{{ name }}！</h1>
    <p>我们已收到您的留言，会尽快回复。</p>
    <a href="/">返回首页</a>
</body>
</html>
```

现在，当用户填写并提交表单时，他们会看到一个个性化的感谢页面，这种交互体验是不是很棒？

## 七、部署你的网站：让全世界都能看到

在本地电脑上运行的网站只有你自己能看到，要让全世界都能访问，我们需要把它「**部署**」到互联网上。

对于初学者来说，**PythonAnywhere** 是一个非常友好的免费托管平台，只需几步就能让你的网站上线。

1. 注册一个 PythonAnywhere 账号（免费版就够用了）
2. 上传你的项目文件
3. 设置一个 Web 应用，指向你的 Flask 应用
4. 点击生成的链接，瞧！你的网站已经可以被全世界访问了！

当你把自己的网站链接分享给朋友时，那种成就感是无与伦比的！

## 总结：你已经迈出了成为 Web 开发者的第一步！

恭喜你！通过这篇教程，你已经从零基础成功搭建了自己的第一个 Flask 网站，这是一个了不起的成就！

我们学习了 Flask 的基础知识，创建了多个页面，添加了样式和交互功能，甚至把网站部署到了互联网上，这些都是专业 Web 开发的核心技能。

记住，每个专业的 Web 开发者都是从第一个 "Hello, World!" 开始的，你已经迈出了重要的第一步！

继续探索 Flask 的更多功能，比如数据库集成、用户认证、API 开发等，你会发现 Web 开发的世界无比广阔和有趣。

下期预告：我们将深入探讨如何将 **SQLite 数据库**集成到你的 Flask 网站中，实现数据的持久化存储，让你的网站功能更加强大！敬请期待！

你有什么想用 Flask 实现的网站创意？欢迎在评论区分享，我们一起讨论如何实现它！