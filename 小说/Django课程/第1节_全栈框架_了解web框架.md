# 第1节：全栈框架_了解web框架

## 来源

Web框架是现代Web开发的基础工具，它们提供了一套结构化的方法来构建Web应用程序。Django作为Python生态系统中最流行的Web框架之一，采用了MVT（Model-View-Template）架构模式，这是对传统MVC（Model-View-Controller）模式的一种变体。了解这些架构模式对于掌握Django框架至关重要。

## 定义

### MVC架构

MVC（Model-View-Controller）是一种软件设计模式，它将应用程序分为三个相互关联的组件：

1. **模型（Model）**：负责数据逻辑和业务规则，直接管理应用程序的数据、逻辑和规则。
2. **视图（View）**：负责用户界面元素，向用户显示数据。
3. **控制器（Controller）**：处理用户输入，协调模型和视图。

### MVT架构

MVT（Model-View-Template）是Django框架采用的架构模式：

1. **模型（Model）**：与MVC中的模型相同，负责数据结构和数据库交互。
2. **视图（View）**：类似于MVC中的控制器，处理业务逻辑并与模型和模板交互。
3. **模板（Template）**：对应MVC中的视图，负责用户界面的表现层。

### 常见Web框架对比

| 框架 | 语言 | 架构模式 | 特点 |
|------|------|----------|-------|
| Django | Python | MVT | 全栈框架，内置管理后台，ORM系统 |
| Flask | Python | 无固定架构 | 轻量级，灵活性高，扩展丰富 |
| Ruby on Rails | Ruby | MVC | 约定优于配置，快速开发 |
| Express.js | JavaScript | MVC | 轻量级，灵活，Node.js平台 |
| Laravel | PHP | MVC | 优雅语法，丰富功能 |

## 案例

### MVC架构示例（伪代码）

```
// 模型（Model）
class User {
    function getUserData(id) {
        // 从数据库获取用户数据
        return userData;
    }
}

// 视图（View）
class UserView {
    function displayUserProfile(userData) {
        // 渲染用户资料页面
        render("user_profile.html", userData);
    }
}

// 控制器（Controller）
class UserController {
    function showUserProfile(userId) {
        // 获取用户数据
        user = new User();
        userData = user.getUserData(userId);
        
        // 显示用户资料
        view = new UserView();
        view.displayUserProfile(userData);
    }
}
```

### MVT架构示例（Django）

```python
# 模型（Model）- models.py
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    
# 视图（View）- views.py
from django.shortcuts import render
from .models import User

def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'user_profile.html', {'user': user})
    
# 模板（Template）- user_profile.html
<html>
<body>
    <h1>{{ user.username }}的个人资料</h1>
    <p>邮箱：{{ user.email }}</p>
</body>
</html>
```

## 创建开发环境

要开始Django开发，需要设置适当的开发环境：

1. **安装Python**：Django是Python框架，首先需要安装Python（推荐3.8+版本）。

2. **创建虚拟环境**：隔离项目依赖，避免冲突。
   ```bash
   python -m venv django_env
   source django_env/bin/activate  # Linux/Mac
   django_env\Scripts\activate  # Windows
   ```

3. **安装Django**：
   ```bash
   pip install django
   ```

4. **验证安装**：
   ```bash
   python -m django --version
   ```

5. **创建项目**：
   ```bash
   django-admin startproject myproject
   cd myproject
   ```

6. **运行开发服务器**：
   ```bash
   python manage.py runserver
   ```
   访问 http://127.0.0.1:8000/ 查看默认欢迎页面。

## 总结

1. **MVC和MVT是Web开发中常用的架构模式**，它们帮助开发者组织代码，实现关注点分离。

2. **Django采用MVT架构**，其中Model负责数据，View处理逻辑，Template负责展示。

3. **不同Web框架有各自的特点和适用场景**，选择框架时应考虑项目需求、团队技能和性能要求。

4. **创建开发环境是开始Django项目的第一步**，包括安装Python、创建虚拟环境和安装Django。

5. **了解框架架构有助于更好地理解Django的工作原理**，为后续学习打下基础。

通过本节课，我们对Web框架的基本概念、MVC与MVT架构模式有了初步了解，并学会了如何搭建Django开发环境。下一节将深入介绍Django项目的基本结构和配置。