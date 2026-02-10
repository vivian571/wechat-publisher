# 第17节：全栈框架_django项目2

## 来源

在上一节中，我们已经完成了博客系统的基本框架搭建，实现了用户注册和登录功能。本节将继续开发这个博客系统，重点完善用户认证相关的功能，包括登录验证、密码重置、密码修改等。这些功能在实际的Web应用程序中非常重要，它们不仅提高了用户体验，还增强了系统的安全性。通过本节的学习，我们将深入了解Django的auth模块的高级功能，以及如何将这些功能集成到我们的博客系统中。

## 定义

### 登录验证

登录验证是确保用户身份的过程，包括验证用户名和密码是否匹配，以及是否有权限访问特定资源。Django的auth模块提供了完善的登录验证机制，包括表单验证、会话管理、权限检查等。

### 密码重置

密码重置是允许用户在忘记密码时重新设置密码的功能。通常包括以下步骤：
1. 用户请求重置密码
2. 系统发送包含重置链接的邮件
3. 用户点击链接进入重置页面
4. 用户设置新密码

### 密码修改

密码修改是允许已登录用户更改自己密码的功能。通常需要用户输入当前密码进行验证，然后设置新密码。

## 案例

### 1. 配置邮件发送

为了实现密码重置功能，我们需要配置邮件发送。在`settings.py`中添加以下配置：

```python
# blog_project/settings.py

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'  # 替换为您的SMTP服务器
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'  # 替换为您的邮箱
EMAIL_HOST_PASSWORD = 'your-password'  # 替换为您的密码
```

对于开发环境，可以使用控制台后端，这样邮件内容会直接打印到控制台，而不是真正发送：

```python
# 开发环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 2. 添加密码重置URL

在`urls.py`中添加密码重置相关的URL：

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
    
    # 密码重置URL
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # 密码修改URL
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
    
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. 创建密码重置模板

创建密码重置请求模板：

```html
<!-- templates/users/password_reset.html -->
{% extends 'base.html' %}

{% block title %}重置密码 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>重置密码</h2>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            <p>忘记密码了？请输入您的电子邮件地址，我们将向您发送重置密码的链接。</p>
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
                            <button class="btn btn-primary" type="submit">发送重置邮件</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

创建密码重置邮件发送成功模板：

```html
<!-- templates/users/password_reset_done.html -->
{% extends 'base.html' %}

{% block title %}邮件已发送 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>邮件已发送</h2>
        </div>
        <div class="card-body">
            <p>我们已经向您的邮箱发送了一封包含重置密码链接的邮件。如果您提供的邮箱地址存在于我们的系统中，您应该很快就能收到这封邮件。</p>
            <p>如果您没有收到邮件，请确认您输入的是注册时使用的邮箱地址，并检查您的垃圾邮件文件夹。</p>
            <a href="{% url 'login' %}">返回登录页面</a>
        </div>
    </div>
{% endblock %}
```

创建密码重置确认模板：

```html
<!-- templates/users/password_reset_confirm.html -->
{% extends 'base.html' %}

{% block title %}设置新密码 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>设置新密码</h2>
                </div>
                <div class="card-body">
                    {% if validlink %}
                        <form method="POST">
                            {% csrf_token %}
                            <fieldset class="form-group">
                                <p>请输入并确认您的新密码。</p>
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
                                <button class="btn btn-primary" type="submit">设置新密码</button>
                            </div>
                        </form>
                    {% else %}
                        <p>密码重置链接无效，可能是因为它已经被使用过或已过期。请重新申请密码重置。</p>
                        <a href="{% url 'password_reset' %}">重新申请密码重置</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

创建密码重置完成模板：

```html
<!-- templates/users/password_reset_complete.html -->
{% extends 'base.html' %}

{% block title %}密码已重置 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>密码已重置</h2>
        </div>
        <div class="card-body">
            <p>您的密码已成功重置。现在您可以使用新密码登录了。</p>
            <a href="{% url 'login' %}" class="btn btn-primary">登录</a>
        </div>
    </div>
{% endblock %}
```

### 4. 创建密码修改模板

创建密码修改模板：

```html
<!-- templates/users/password_change.html -->
{% extends 'base.html' %}

{% block title %}修改密码 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>修改密码</h2>
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
                            <button class="btn btn-primary" type="submit">修改密码</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

创建密码修改完成模板：

```html
<!-- templates/users/password_change_done.html -->
{% extends 'base.html' %}

{% block title %}密码已修改 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>密码已修改</h2>
        </div>
        <div class="card-body">
            <p>您的密码已成功修改。</p>
            <a href="{% url 'profile' %}" class="btn btn-primary">返回个人资料</a>
        </div>
    </div>
{% endblock %}
```

### 5. 更新个人资料页面

在个人资料页面添加密码修改链接：

```html
<!-- templates/users/profile.html -->
<!-- 在个人资料卡片中添加 -->
<div class="card-footer">
    <a href="{% url 'password_change' %}" class="btn btn-secondary">修改密码</a>
</div>
```

### 6. 更新登录页面

在登录页面添加密码重置链接：

```html
<!-- templates/users/login.html -->
<!-- 在表单下方添加 -->
<div class="border-top pt-3">
    <small class="text-muted">
        忘记密码？ <a href="{% url 'password_reset' %}">重置密码</a>
    </small>
</div>
```

### 7. 添加登录验证

为了确保只有登录用户才能访问某些页面，我们可以使用Django的`login_required`装饰器。我们已经在上一节中为个人资料页面添加了这个装饰器，现在让我们为博客应用添加一些需要登录才能访问的功能。

首先，创建一个新的视图函数，用于创建新文章：

```python
# blog/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostForm

def home(request):
    posts = Post.objects.all().order_by('-date_posted')
    return render(request, 'blog/home.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '文章已成功发布！')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})
```

创建文章模型和表单：

```python
# blog/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
```

```python
# blog/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.post_create, name='post_create'),
]
```

创建文章表单模板：

```html
<!-- templates/blog/post_form.html -->
{% extends 'base.html' %}

{% block title %}发布文章 - 博客系统{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>发布新文章</h2>
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
                            <button class="btn btn-primary" type="submit">发布</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

更新导航栏，添加发布文章链接：

```html
<!-- templates/base.html -->
<!-- 在导航栏中添加 -->
{% if user.is_authenticated %}
    <li class="nav-item">
        <a class="nav-link" href="{% url 'post_create' %}">发布文章</a>
    </li>
{% endif %}
```

### 8. 运行迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

## 总结

1. **密码重置功能是用户认证系统的重要组成部分**，它允许用户在忘记密码时通过邮件重置密码，提高了系统的可用性。

2. **密码修改功能允许已登录用户更改自己的密码**，增强了账户安全性，是用户管理自己账户的重要工具。

3. **登录验证是保护敏感资源的重要机制**，通过`login_required`装饰器可以轻松实现对特定视图的访问控制。

4. **Django的auth模块提供了完善的用户认证功能**，包括密码重置、密码修改、登录验证等，大大简化了开发工作。

5. **邮件发送是密码重置功能的关键**，Django提供了灵活的邮件后端配置，支持多种邮件发送方式。

6. **模板系统使前端开发更加灵活**，通过创建不同的模板，可以为用户提供一致且友好的界面。

7. **消息框架提供了一种向用户显示通知的方式**，如操作成功、错误提示等，提高了用户体验。

8. **URL配置是连接视图和模板的桥梁**，通过合理的URL设计，可以提高系统的可用性和可维护性。

通过本节的学习，我们已经完善了博客系统的用户认证功能，包括密码重置、密码修改、登录验证等。在下一节中，我们将继续开发这个博客系统，添加更多功能，如文章详情页、文章编辑和删除等。