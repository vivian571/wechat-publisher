# 第2节：全栈框架_django

## 来源

Django是一个由Python编写的开源Web框架，最初由Adrian Holovaty和Simon Willison于2003年开发，2005年7月作为开源项目发布。Django的名字来源于著名的爵士吉他手Django Reinhardt，体现了这个框架优雅而强大的特性。Django的设计理念是"DRY"（Don't Repeat Yourself，不要重复自己）和"快速开发"，它提供了丰富的功能和工具，使开发者能够快速构建安全、可维护的Web应用程序。

## 定义

### Django项目主要文件介绍

当你创建一个新的Django项目时，Django会自动生成一系列文件和目录，构成项目的基本结构：

1. **manage.py**：一个命令行工具，用于与Django项目进行交互。通过它可以运行开发服务器、创建数据库表、执行数据迁移等操作。

2. **项目包目录**（与项目同名的目录）：
   - **__init__.py**：空文件，表明该目录是一个Python包。
   - **settings.py**：项目的配置文件，包含数据库配置、中间件设置、静态文件路径等。
   - **urls.py**：URL声明文件，定义了URL与视图函数的映射关系。
   - **asgi.py**：ASGI（Asynchronous Server Gateway Interface）配置，用于异步Web服务器。
   - **wsgi.py**：WSGI（Web Server Gateway Interface）配置，用于部署Django应用到生产环境。

### Django与如图关系数据库的交互

Django提供了强大的ORM（对象关系映射）系统，使开发者可以通过Python代码操作数据库，而不需要直接编写SQL语句：

1. **模型定义**：在`models.py`文件中定义数据模型类，每个类对应数据库中的一个表。

2. **数据库迁移**：Django的迁移系统会自动生成SQL语句，创建或修改数据库表结构。
   - `python manage.py makemigrations`：创建迁移文件
   - `python manage.py migrate`：应用迁移到数据库

3. **查询API**：Django ORM提供了丰富的查询API，用于增删改查操作。
   - `Model.objects.create()`：创建记录
   - `Model.objects.filter()`：查询记录
   - `Model.objects.update()`：更新记录
   - `Model.objects.delete()`：删除记录

### Django路由配置

Django的URL配置系统（也称为URLconf）定义了URL模式与视图函数的映射关系：

1. **项目级URLs**：在项目的`urls.py`文件中定义主要URL模式，通常会将请求分发到各个应用的URL配置。

2. **应用级URLs**：每个应用可以有自己的`urls.py`文件，定义该应用特定的URL模式。

3. **URL模式**：使用正则表达式或简化的路径模式定义URL，并将其映射到视图函数。

### 静态文件的配置与引用

Django将静态文件（CSS、JavaScript、图片等）与模板分开管理：

1. **静态文件配置**：在`settings.py`中配置静态文件目录和URL前缀。
   ```python
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   ```

2. **静态文件组织**：通常在项目或应用目录下创建`static`目录，按类型组织静态文件。
   ```
   static/
       css/
           style.css
       js/
           script.js
       images/
           logo.png
   ```

3. **在模板中引用**：使用`{% static %}`模板标签引用静态文件。
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/style.css' %}">
   ```

## 案例

### 创建Django项目和应用

```bash
# 创建项目
python -m django-admin startproject mysite
cd mysite

# 创建应用
python manage.py startapp blog
```

### 项目结构示例

```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
    blog/
        __init__.py
        admin.py
        apps.py
        migrations/
        models.py
        tests.py
        views.py
        urls.py
    static/
        css/
        js/
        images/
    templates/
```

### 配置数据库（settings.py）

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 数据库引擎
        'NAME': BASE_DIR / 'db.sqlite3',         # 数据库文件路径
    }
}
```

### 定义模型（blog/models.py）

```python
from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
```

### 配置URL（mysite/urls.py）

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]
```

### 应用URL配置（blog/urls.py）

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
]
```

### 静态文件配置与使用

```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

```html
<!-- templates/blog/base.html -->
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>My Blog</title>
    <link rel="stylesheet" href="{% static 'css/blog.css' %}">
</head>
<body>
    <div class="page-header">
        <h1><a href="/">Django Blog</a></h1>
    </div>
    <div class="content">
        {% block content %}
        {% endblock %}
    </div>
</body>
</html>
```

## 总结

1. **Django项目结构清晰**，包含管理脚本、配置文件、URL配置等核心组件，便于组织和维护代码。

2. **Django ORM提供了强大的数据库抽象层**，使开发者可以通过Python代码操作数据库，避免直接编写SQL语句。

3. **URL配置系统灵活**，支持项目级和应用级URL配置，可以使用正则表达式或简化的路径模式定义URL。

4. **静态文件管理系统**使CSS、JavaScript和图片等资源的组织和引用变得简单高效。

5. **Django遵循"电池已包含"的理念**，提供了Web开发所需的大部分功能，但同时也保持了足够的灵活性，允许开发者根据需求进行定制。

通过本节课，我们了解了Django项目的基本结构和配置方法，包括文件组织、数据库配置、URL配置和静态文件管理。这些知识为我们后续深入学习Django框架奠定了基础。下一节将介绍Django的路由层，探讨URL配置的更多细节。