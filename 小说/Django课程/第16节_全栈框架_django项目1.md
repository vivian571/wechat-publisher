# 第16节：全栈框架_django项目1

## 来源

在学习了Django框架的各个组件和功能后，我们需要将这些知识整合起来，开发一个完整的Web应用程序。本节将开始一个实际的Django项目开发，通过实践来巩固之前学习的内容，并了解如何将不同的组件组合在一起构建一个功能完整的Web应用。我们将从项目的初始化开始，逐步实现用户注册和登录功能，这是大多数Web应用程序的基础功能。通过这个项目，我们将学习如何使用Django的auth模块、表单系统、模板系统等组件，以及如何组织项目结构，使代码更加清晰和可维护。这个项目将贯穿后续几节内容，逐步添加更多功能，最终形成一个完整的Web应用程序。

## 定义

### 项目概述

我们将开发一个博客系统，用户可以注册账号、登录、发布文章、评论文章等。本节将重点实现用户注册和登录功能，为后续功能开发打下基础。

### 项目初始化

首先，我们需要创建一个新的Django项目和应用：

```bash
# 创建项目
django-admin startproject blog_project

# 进入项目目录
cd blog_project

# 创建应用
python manage.py startapp users
python manage.py startapp blog
```

### 项目结构

初始化后的项目结构如下：

```
blog_project/
    manage.py
    blog_project/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
    users/
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
        migrations/
    blog/
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
        migrations/
```

### 配置项目

在`settings.py`中添加我们创建的应用：

```python
# blog_project/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',  # 添加users应用
    'blog.apps.BlogConfig',    # 添加blog应用
]

# 设置登录和注销后的重定向URL
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# 设置媒体文件路径
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 案例

### 1. 创建用户模型

我们将扩展Django的内置用户模型，添加额外的字段：

```python
# users/models.py
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # 调整头像大小
        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)
```

### 2. 创建信号以自动创建用户资料

当新用户注册时，我们希望自动为其创建一个资料：

```python
# users/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
```

在应用的`apps.py`中注册信号：

```python
# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        import users.signals
```

### 3. 创建用户注册表单

```python
# users/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
```

### 4. 创建视图函数

```python
# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号已创建，现在可以登录了！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'您的账号已更新！')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)
```

### 5. 创建URL配置

```python
# blog_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
```

### 6. 创建基本视图

```python
# blog/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'blog/home.html')
```

### 7. 创建模板

首先，创建基础模板：

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}博客系统{% endblock %}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            padding-top: 56px;
        }
        .content {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">博客系统</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarContent">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarContent">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'home' %}">首页</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'profile' %}">个人资料</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'logout' %}">注销</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'register' %}">注册</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    
    <main class="container content">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
```

然后，创建首页模板：

```html
<!-- templates/blog/home.html -->
{% extends 'base.html' %}

{% block title %}首页 - 博客系统{% endblock %}

{% block content %}
    <div class="jumbotron">
        <h1 class="display-4">欢迎来到博客系统</h1>
        <p class="lead">这是一个使用Django开发的博客系统，您可以在这里分享您的想法和经验。</p>
        <hr class="my-4">
        <p>立即注册账号，开始您的博客之旅！</p>
        {% if not user.is_authenticated %}
            <a class="btn btn-primary btn-lg" href="{% url 'register' %}" role="button">注册</a>
        {% endif %}
    </div>
{% endblock %}
```

创建用户注册模板：

```html
<!-- templates/users/register.html -->
{% extends 'base.html' %}

{% block title %}注册 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>注册</h2>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            {% for field in form %}
                                <div class="form-group">
                                    {{ field.label_tag }}
                                    {{ field }}
                                    {% if field.errors %}
                                        <div class="text-danger">
                                            {% for error in field.errors %}
                                                {{ error }}
                                            {% endfor %}
                                        </div>
                                    {% endif %}
                                    {% if field.help_text %}
                                        <small class="form-text text-muted">{{ field.help_text }}</small>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </fieldset>
                        <div class="form-group">
                            <button class="btn btn-primary" type="submit">注册</button>
                        </div>
                    </form>
                    <div class="border-top pt-3">
                        <small class="text-muted">
                            已有账号？ <a class="ml-2" href="{% url 'login' %}">登录</a>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

创建登录模板：

```html
<!-- templates/users/login.html -->
{% extends 'base.html' %}

{% block title %}登录 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>登录</h2>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            {% for field in form %}
                                <div class="form-group">
                                    {{ field.label_tag }}
                                    {{ field }}
                                    {% if field.errors %}
                                        <div class="text-danger">
                                            {% for error in field.errors %}
                                                {{ error }}
                                            {% endfor %}
                                        </div>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </fieldset>
                        <div class="form-group">
                            <button class="btn btn-primary" type="submit">登录</button>
                        </div>
                    </form>
                    <div class="border-top pt-3">
                        <small class="text-muted">
                            需要一个账号？ <a class="ml-2" href="{% url 'register' %}">注册</a>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

创建注销模板：

```html
<!-- templates/users/logout.html -->
{% extends 'base.html' %}

{% block title %}注销 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>您已注销</h2>
        </div>
        <div class="card-body">
            <p>感谢您的访问，您已成功注销。</p>
            <a href="{% url 'login' %}">重新登录</a>
        </div>
    </div>
{% endblock %}
```

创建个人资料模板：

```html
<!-- templates/users/profile.html -->
{% extends 'base.html' %}

{% block title %}个人资料 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h3>{{ user.username }}</h3>
                </div>
                <div class="card-body text-center">
                    <img class="rounded-circle img-fluid" src="{{ user.profile.avatar.url }}" alt="用户头像">
                    <p class="mt-3">{{ user.profile.bio }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>更新个人资料</h3>
                </div>
                <div class="card-body">
                    <form method="POST" enctype="multipart/form-data">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            <legend class="border-bottom mb-4">个人信息</legend>
                            {% for field in u_form %}
                                <div class="form-group">
                                    {{ field.label_tag }}
                                    {{ field }}
                                    {% if field.errors %}
                                        <div class="text-danger">
                                            {% for error in field.errors %}
                                                {{ error }}
                                            {% endfor %}
                                        </div>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </fieldset>
                        <fieldset class="form-group">
                            <legend class="border-bottom mb-4">个人资料</legend>
                            {% for field in p_form %}
                                <div class="form-group">
                                    {{ field.label_tag }}
                                    {{ field }}
                                    {% if field.errors %}
                                        <div class="text-danger">
                                            {% for error in field.errors %}
                                                {{ error }}
                                            {% endfor %}
                                        </div>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </fieldset>
                        <div class="form-group">
                            <button class="btn btn-primary" type="submit">更新</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

### 8. 配置模板目录

在`settings.py`中配置模板目录：

```python
# blog_project/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 添加这一行
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 9. 运行迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 10. 创建超级用户

```bash
python manage.py createsuperuser
```

### 11. 运行开发服务器

```bash
python manage.py runserver
```

## 总结

1. **项目初始化是Django开发的第一步**，包括创建项目、创建应用、配置设置等，为后续开发奠定基础。

2. **用户认证是Web应用程序的基础功能**，Django的auth模块提供了完善的用户认证系统，包括用户注册、登录、注销等功能。

3. **扩展用户模型可以添加额外的用户信息**，如个人简介、头像等，使用户资料更加丰富。

4. **信号机制可以在特定事件发生时自动执行操作**，如在用户创建时自动创建用户资料。

5. **表单系统简化了用户输入的处理**，包括数据验证、错误处理等，提高了开发效率。

6. **模板系统使前端开发更加灵活**，通过模板继承、变量传递等机制，可以创建一致的用户界面。

7. **消息框架提供了一种向用户显示通知的方式**，如操作成功、错误提示等，提高了用户体验。

8. **静态文件和媒体文件的处理是Web开发的重要部分**，Django提供了简单的方式来管理这些文件。

通过本节的学习，我们已经实现了一个基本的用户认证系统，包括用户注册、登录、注销和个人资料管理等功能。在下一节中，我们将继续开发这个博客系统，添加文章发布、列表显示等功能。