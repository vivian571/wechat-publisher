# 第18节：全栈框架_django项目3

## 来源

在前两节中，我们已经完成了博客系统的基本框架搭建，实现了用户注册、登录、密码重置等功能，并添加了发布文章的功能。本节将继续开发这个博客系统，重点实现文章详情页、文章编辑和删除功能，以及用户个人文章管理功能。这些功能是博客系统的核心部分，它们让用户能够完整地管理自己的文章内容，提高了系统的实用性和用户体验。

## 定义

### 文章详情页

文章详情页是展示单篇文章完整内容的页面，通常包括文章标题、内容、作者信息、发布时间等。在博客系统中，文章详情页是用户阅读文章的主要入口，也是评论、分享等交互功能的载体。

### 文章编辑

文章编辑功能允许作者修改已发布的文章内容，包括标题、正文等。这个功能通常只对文章的原作者开放，确保内容的安全性和完整性。

### 文章删除

文章删除功能允许作者删除不再需要的文章。同样，这个功能通常只对文章的原作者开放，并且可能需要确认步骤以防止误操作。

### 用户个人文章管理

用户个人文章管理是一个集中展示和管理用户所有文章的功能，通常包括文章列表、编辑入口、删除选项等，方便用户统一管理自己的内容。

## 案例

### 1. 创建文章详情页

首先，我们需要创建一个视图函数来处理文章详情页的请求：

```python
# blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})
```

然后，更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
]
```

创建文章详情页模板：

```html
<!-- templates/blog/post_detail.html -->
{% extends 'base.html' %}

{% block title %}{{ post.title }} - 博客系统{% endblock %}

{% block content %}
    <div class="card mb-4">
        <div class="card-header">
            <h2 class="card-title">{{ post.title }}</h2>
            <small class="text-muted">由 {{ post.author.username }} 发布于 {{ post.date_posted|date:"Y-m-d H:i" }}</small>
        </div>
        <div class="card-body">
            <p class="card-text">{{ post.content|linebreaks }}</p>
        </div>
        {% if user == post.author %}
            <div class="card-footer">
                <a href="{% url 'post_update' post.pk %}" class="btn btn-secondary">编辑</a>
                <a href="{% url 'post_delete' post.pk %}" class="btn btn-danger">删除</a>
            </div>
        {% endif %}
    </div>
{% endblock %}
```

更新首页模板，添加文章详情页链接：

```html
<!-- templates/blog/home.html -->
<!-- 在文章标题处添加链接 -->
<h2 class="card-title"><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
```

### 2. 实现文章编辑功能

添加文章编辑视图：

```python
# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostForm

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查当前用户是否是文章作者
    if post.author != request.user:
        messages.error(request, '您没有权限编辑这篇文章！')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '文章已成功更新！')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': '编辑文章'})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/update/', views.post_update, name='post_update'),
]
```

### 3. 实现文章删除功能

添加文章删除视图：

```python
# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查当前用户是否是文章作者
    if post.author != request.user:
        messages.error(request, '您没有权限删除这篇文章！')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '文章已成功删除！')
        return redirect('home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/update/', views.post_update, name='post_update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
]
```

创建文章删除确认模板：

```html
<!-- templates/blog/post_confirm_delete.html -->
{% extends 'base.html' %}

{% block title %}删除文章 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>删除文章</h2>
        </div>
        <div class="card-body">
            <form method="POST">
                {% csrf_token %}
                <fieldset class="form-group">
                    <p>您确定要删除文章 "{{ post.title }}" 吗？此操作不可撤销！</p>
                </fieldset>
                <div class="form-group">
                    <button class="btn btn-danger" type="submit">确认删除</button>
                    <a class="btn btn-secondary" href="{% url 'post_detail' post.pk %}">取消</a>
                </div>
            </form>
        </div>
    </div>
{% endblock %}
```

### 4. 实现用户个人文章管理

添加用户文章列表视图：

```python
# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Post

def user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-date_posted')
    return render(request, 'blog/user_posts.html', {'posts': posts, 'author': user})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/update/', views.post_update, name='post_update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('user/<str:username>/', views.user_posts, name='user_posts'),
]
```

创建用户文章列表模板：

```html
<!-- templates/blog/user_posts.html -->
{% extends 'base.html' %}

{% block title %}{{ author.username }}的文章 - 博客系统{% endblock %}

{% block content %}
    <h1 class="mb-4">{{ author.username }}的文章 ({{ posts.count }})</h1>
    {% if posts %}
        {% for post in posts %}
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="card-title"><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
                    <small class="text-muted">发布于 {{ post.date_posted|date:"Y-m-d H:i" }}</small>
                </div>
                <div class="card-body">
                    <p class="card-text">{{ post.content|truncatewords:50 }}</p>
                    <a href="{% url 'post_detail' post.pk %}" class="btn btn-primary">阅读全文</a>
                    {% if user == post.author %}
                        <a href="{% url 'post_update' post.pk %}" class="btn btn-secondary">编辑</a>
                        <a href="{% url 'post_delete' post.pk %}" class="btn btn-danger">删除</a>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info">该用户还没有发布任何文章。</div>
    {% endif %}
{% endblock %}
```

更新首页和文章详情页，添加作者链接：

```html
<!-- templates/blog/home.html 和 templates/blog/post_detail.html -->
<!-- 将作者名称改为链接 -->
<small class="text-muted">由 <a href="{% url 'user_posts' post.author.username %}">{{ post.author.username }}</a> 发布于 {{ post.date_posted|date:"Y-m-d H:i" }}</small>
```

更新个人资料页面，添加查看个人文章的链接：

```html
<!-- templates/users/profile.html -->
<!-- 在个人资料卡片中添加 -->
<div class="card-footer">
    <a href="{% url 'password_change' %}" class="btn btn-secondary">修改密码</a>
    <a href="{% url 'user_posts' user.username %}" class="btn btn-primary">我的文章</a>
</div>
```

### 5. 添加分页功能

为了提高用户体验，我们可以为首页和用户文章列表添加分页功能：

```python
# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Post

def home(request):
    posts = Post.objects.all().order_by('-date_posted')
    paginator = Paginator(posts, 5)  # 每页显示5篇文章
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/home.html', {'posts': posts})

def user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=user).order_by('-date_posted')
    paginator = Paginator(posts_list, 5)  # 每页显示5篇文章
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/user_posts.html', {'posts': posts, 'author': user})
```

创建分页导航模板：

```html
<!-- templates/blog/pagination.html -->
{% if posts.has_other_pages %}
    <nav aria-label="分页导航">
        <ul class="pagination justify-content-center">
            {% if posts.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page=1">&laquo; 首页</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ posts.previous_page_number }}">上一页</a>
                </li>
            {% else %}
                <li class="page-item disabled">
                    <span class="page-link">&laquo; 首页</span>
                </li>
                <li class="page-item disabled">
                    <span class="page-link">上一页</span>
                </li>
            {% endif %}
            
            {% for num in posts.paginator.page_range %}
                {% if posts.number == num %}
                    <li class="page-item active">
                        <span class="page-link">{{ num }}</span>
                    </li>
                {% elif num > posts.number|add:'-3' and num < posts.number|add:'3' %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                    </li>
                {% endif %}
            {% endfor %}
            
            {% if posts.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ posts.next_page_number }}">下一页</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ posts.paginator.num_pages }}">末页 &raquo;</a>
                </li>
            {% else %}
                <li class="page-item disabled">
                    <span class="page-link">下一页</span>
                </li>
                <li class="page-item disabled">
                    <span class="page-link">末页 &raquo;</span>
                </li>
            {% endif %}
        </ul>
    </nav>
{% endif %}
```

在首页和用户文章列表页面中包含分页导航：

```html
<!-- templates/blog/home.html 和 templates/blog/user_posts.html -->
<!-- 在文章列表下方添加 -->
{% include 'blog/pagination.html' %}
```

## 总结

1. **文章详情页是博客系统的核心功能**，它展示文章的完整内容，是用户阅读和交互的主要入口。

2. **文章编辑和删除功能让作者能够管理自己的内容**，但需要进行权限控制，确保只有文章作者才能执行这些操作。

3. **用户个人文章管理功能提供了集中管理文章的方式**，方便用户查看和管理自己发布的所有文章。

4. **分页功能提高了用户体验**，特别是在文章数量较多的情况下，可以避免页面加载过慢和信息过载。

5. **URL设计是Web应用程序的重要部分**，合理的URL结构可以提高系统的可用性和SEO效果。

6. **模板继承和包含机制使前端开发更加模块化**，可以避免代码重复，提高开发效率。

7. **权限控制是Web应用程序安全的重要组成部分**，通过检查用户身份和权限，可以防止未授权的操作。

8. **消息框架提供了一种向用户显示通知的方式**，如操作成功、错误提示等，提高了用户体验。

通过本节的学习，我们已经实现了博客系统的核心功能，包括文章详情页、文章编辑和删除、用户个人文章管理等。在下一节中，我们将继续开发这个博客系统，添加评论功能，让用户能够在文章下方发表评论，增强系统的互动性。