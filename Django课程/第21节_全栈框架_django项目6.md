# 第21节：全栈框架_django项目6

## 来源

在前五节中，我们已经完成了博客系统的基本框架搭建，实现了用户认证、文章管理、评论功能、搜索功能和标签功能。本节将继续开发这个博客系统，重点实现一些高级功能，如文章点赞、收藏、分享等，进一步提升系统的互动性和用户体验。这些功能在现代社交媒体和内容平台中非常常见，它们不仅增强了用户参与度，还提供了内容传播和用户反馈的渠道。

## 定义

### 文章点赞

文章点赞是一种简单的用户反馈机制，允许用户表达对内容的喜欢或支持。在博客系统中，点赞功能通常以计数器的形式展示，显示有多少用户喜欢这篇文章。

### 文章收藏

文章收藏允许用户保存感兴趣的文章，以便日后查看。这个功能类似于浏览器的书签功能，但它是在应用程序内部实现的，通常会在用户的个人页面中显示收藏的文章列表。

### 文章分享

文章分享功能允许用户将内容分享到社交媒体平台或通过其他渠道（如电子邮件、消息应用等）分享给朋友。这个功能通常通过社交媒体平台提供的分享API或简单的链接复制功能实现。

## 案例

### 1. 实现文章点赞功能

首先，我们需要创建一个模型来存储点赞信息：

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # 现有的Post模型代码...
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    def total_likes(self):
        return self.likes.count()
```

创建点赞视图：

```python
# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查用户是否已经点赞
    if post.likes.filter(id=request.user.id).exists():
        # 如果已经点赞，则取消点赞
        post.likes.remove(request.user)
        liked = False
    else:
        # 如果没有点赞，则添加点赞
        post.likes.add(request.user)
        liked = True
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes()
        })
    
    # 如果不是AJAX请求，重定向回文章详情页
    return redirect('post_detail', pk=post.pk)
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有的URL配置...
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
]
```

更新文章详情模板，添加点赞按钮：

```html
<!-- templates/blog/post_detail.html -->
<!-- 在文章内容下方添加 -->
<div class="mt-3">
    <form action="{% url 'like_post' post.pk %}" method="POST" class="like-form" data-post-id="{{ post.pk }}">
        {% csrf_token %}
        <button type="submit" class="btn btn-sm {% if user in post.likes.all %}btn-danger{% else %}btn-outline-danger{% endif %}">
            <i class="fas fa-heart"></i> 
            <span class="like-count">{{ post.total_likes }}</span> 喜欢
        </button>
    </form>
</div>
```

添加JavaScript代码，实现AJAX点赞：

```html
<!-- templates/blog/post_detail.html -->
{% block extra_js %}
<script>
    // 处理点赞功能的JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        const likeForms = document.querySelectorAll('.like-form');
        
        likeForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const postId = this.getAttribute('data-post-id');
                const likeButton = this.querySelector('button');
                const likeCount = this.querySelector('.like-count');
                
                fetch(`/post/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.querySelector('input[name="csrfmiddlewaretoken"]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // 更新点赞按钮样式
                    if (data.liked) {
                        likeButton.classList.remove('btn-outline-danger');
                        likeButton.classList.add('btn-danger');
                    } else {
                        likeButton.classList.remove('btn-danger');
                        likeButton.classList.add('btn-outline-danger');
                    }
                    
                    // 更新点赞数量
                    likeCount.textContent = data.total_likes;
                })
                .catch(error => console.error('Error:', error));
            });
        });
    });
</script>
{% endblock %}
```

### 2. 实现文章收藏功能

首先，我们需要创建一个模型来存储收藏信息：

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # 现有的Post模型代码...
    favorites = models.ManyToManyField(User, related_name='favorite_posts', blank=True)
    
    def total_favorites(self):
        return self.favorites.count()
```

创建收藏视图：

```python
# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post

@login_required
def favorite_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查用户是否已经收藏
    if post.favorites.filter(id=request.user.id).exists():
        # 如果已经收藏，则取消收藏
        post.favorites.remove(request.user)
        favorited = False
    else:
        # 如果没有收藏，则添加收藏
        post.favorites.add(request.user)
        favorited = True
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'favorited': favorited,
            'total_favorites': post.total_favorites()
        })
    
    # 如果不是AJAX请求，重定向回文章详情页
    return redirect('post_detail', pk=post.pk)
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有的URL配置...
    path('post/<int:pk>/favorite/', views.favorite_post, name='favorite_post'),
]
```

更新文章详情模板，添加收藏按钮：

```html
<!-- templates/blog/post_detail.html -->
<!-- 在点赞按钮旁边添加 -->
<form action="{% url 'favorite_post' post.pk %}" method="POST" class="favorite-form d-inline-block ml-2" data-post-id="{{ post.pk }}">
    {% csrf_token %}
    <button type="submit" class="btn btn-sm {% if user in post.favorites.all %}btn-warning{% else %}btn-outline-warning{% endif %}">
        <i class="fas fa-bookmark"></i> 
        <span class="favorite-count">{{ post.total_favorites }}</span> 收藏
    </button>
</form>
```

添加JavaScript代码，实现AJAX收藏：

```html
<!-- templates/blog/post_detail.html -->
{% block extra_js %}
<script>
    // 现有的点赞JavaScript代码...
    
    // 处理收藏功能的JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        const favoriteForms = document.querySelectorAll('.favorite-form');
        
        favoriteForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const postId = this.getAttribute('data-post-id');
                const favoriteButton = this.querySelector('button');
                const favoriteCount = this.querySelector('.favorite-count');
                
                fetch(`/post/${postId}/favorite/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.querySelector('input[name="csrfmiddlewaretoken"]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // 更新收藏按钮样式
                    if (data.favorited) {
                        favoriteButton.classList.remove('btn-outline-warning');
                        favoriteButton.classList.add('btn-warning');
                    } else {
                        favoriteButton.classList.remove('btn-warning');
                        favoriteButton.classList.add('btn-outline-warning');
                    }
                    
                    // 更新收藏数量
                    favoriteCount.textContent = data.total_favorites;
                })
                .catch(error => console.error('Error:', error));
            });
        });
    });
</script>
{% endblock %}
```

创建用户收藏列表视图：

```python
# blog/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_favorites(request):
    favorite_posts = request.user.favorite_posts.all().order_by('-date_posted')
    return render(request, 'blog/user_favorites.html', {'posts': favorite_posts})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有的URL配置...
    path('favorites/', views.user_favorites, name='user_favorites'),
]
```

创建用户收藏列表模板：

```html
<!-- templates/blog/user_favorites.html -->
{% extends 'base.html' %}

{% block title %}我的收藏 - 博客系统{% endblock %}

{% block content %}
    <h1 class="mb-4">我的收藏</h1>
    
    {% if posts %}
        {% for post in posts %}
            <div class="card mb-4">
                <div class="card-header">
                    <h2 class="card-title"><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
                    <small class="text-muted">由 <a href="{% url 'user_posts' post.author.username %}">{{ post.author.username }}</a> 发布于 {{ post.date_posted|date:"Y-m-d H:i" }}</small>
                </div>
                <div class="card-body">
                    <p class="card-text">{{ post.content|truncatewords:50 }}</p>
                    <a href="{% url 'post_detail' post.pk %}" class="btn btn-primary">阅读全文</a>
                    <form action="{% url 'favorite_post' post.pk %}" method="POST" class="favorite-form d-inline-block ml-2" data-post-id="{{ post.pk }}">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-warning">
                            <i class="fas fa-bookmark"></i> 取消收藏
                        </button>
                    </form>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info">您还没有收藏任何文章。</div>
    {% endif %}
    
    <div class="mt-4">
        <a href="{% url 'home' %}" class="btn btn-secondary">返回首页</a>
    </div>
{% endblock %}
```

在导航栏中添加收藏链接：

```html
<!-- templates/base.html -->
<!-- 在导航栏中添加 -->
{% if user.is_authenticated %}
    <li class="nav-item">
        <a class="nav-link" href="{% url 'user_favorites' %}">我的收藏</a>
    </li>
{% endif %}
```

### 3. 实现文章分享功能

为了实现文章分享功能，我们可以使用社交媒体平台提供的分享按钮或简单的链接复制功能：

```html
<!-- templates/blog/post_detail.html -->
<!-- 在点赞和收藏按钮旁边添加 -->
<div class="share-buttons mt-3">
    <strong>分享到：</strong>
    <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.build_absolute_uri }}" target="_blank" class="btn btn-sm btn-primary">
        <i class="fab fa-facebook-f"></i> Facebook
    </a>
    <a href="https://twitter.com/intent/tweet?url={{ request.build_absolute_uri }}&text={{ post.title }}" target="_blank" class="btn btn-sm btn-info">
        <i class="fab fa-twitter"></i> Twitter
    </a>
    <a href="https://www.linkedin.com/shareArticle?mini=true&url={{ request.build_absolute_uri }}&title={{ post.title }}" target="_blank" class="btn btn-sm btn-secondary">
        <i class="fab fa-linkedin-in"></i> LinkedIn
    </a>
    <button class="btn btn-sm btn-success copy-link" data-url="{{ request.build_absolute_uri }}">
        <i class="fas fa-link"></i> 复制链接
    </button>
</div>
```

添加JavaScript代码，实现链接复制功能：

```html
<!-- templates/blog/post_detail.html -->
{% block extra_js %}
<script>
    // 现有的点赞和收藏JavaScript代码...
    
    // 处理链接复制功能的JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        const copyLinkButton = document.querySelector('.copy-link');
        
        if (copyLinkButton) {
            copyLinkButton.addEventListener('click', function() {
                const url = this.getAttribute('data-url');
                
                // 创建一个临时输入框
                const tempInput = document.createElement('input');
                tempInput.value = url;
                document.body.appendChild(tempInput);
                
                // 选择并复制文本
                tempInput.select();
                document.execCommand('copy');
                
                // 移除临时输入框
                document.body.removeChild(tempInput);
                
                // 显示复制成功提示
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> 已复制';
                
                // 恢复原始文本
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        }
    });
</script>
{% endblock %}
```

### 4. 添加Font Awesome图标

为了使用上面代码中的图标，我们需要在基础模板中引入Font Awesome：

```html
<!-- templates/base.html -->
<!-- 在head部分添加 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
```

### 5. 运行迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 添加用户活动记录功能

为了跟踪用户的活动，我们可以创建一个活动记录模型：

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=[
        ('view', '查看'),
        ('like', '点赞'),
        ('favorite', '收藏'),
        ('comment', '评论'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
    
    def __str__(self):
        return f'{self.user.username} {self.get_activity_type_display()} {self.post.title}'
```

更新视图，记录用户活动：

```python
# blog/views.py
from .models import UserActivity

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 记录查看活动
    if request.user.is_authenticated:
        UserActivity.objects.create(
            user=request.user,
            post=post,
            activity_type='view'
        )
    
    # 现有的代码...

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查用户是否已经点赞
    if post.likes.filter(id=request.user.id).exists():
        # 如果已经点赞，则取消点赞
        post.likes.remove(request.user)
        liked = False
    else:
        # 如果没有点赞，则添加点赞
        post.likes.add(request.user)
        liked = True
        
        # 记录点赞活动
        UserActivity.objects.create(
            user=request.user,
            post=post,
            activity_type='like'
        )
    
    # 现有的代码...

@login_required
def favorite_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 检查用户是否已经收藏
    if post.favorites.filter(id=request.user.id).exists():
        # 如果已经收藏，则取消收藏
        post.favorites.remove(request.user)
        favorited = False
    else:
        # 如果没有收藏，则添加收藏
        post.favorites.add(request.user)
        favorited = True
        
        # 记录收藏活动
        UserActivity.objects.create(
            user=request.user,
            post=post,
            activity_type='favorite'
        )
    
    # 现有的代码...
```

创建用户活动记录视图：

```python
# blog/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_activities(request):
    activities = request.user.activities.all()[:50]  # 只显示最近50条活动
    return render(request, 'blog/user_activities.html', {'activities': activities})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有的URL配置...
    path('activities/', views.user_activities, name='user_activities'),
]
```

创建用户活动记录模板：

```html
<!-- templates/blog/user_activities.html -->
{% extends 'base.html' %}

{% block title %}我的活动 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>我的活动</h2>
        </div>
        <div class="card-body">
            {% if activities %}
                <div class="list-group">
                    {% for activity in activities %}
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">{{ activity.get_activity_type_display }} <a href="{% url 'post_detail' activity.post.pk %}">{{ activity.post.title }}</a></h5>
                                <small>{{ activity.timestamp|date:"Y-m-d H:i" }}</small>
                            </div>
                            <p class="mb-1">文章作者: <a href="{% url 'user_posts' activity.post.author.username %}">{{ activity.post.author.username }}</a></p>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p>暂无活动记录。</p>
            {% endif %}
        </div>
    </div>
{% endblock %}
```

在导航栏中添加活动记录链接：

```html
<!-- templates/base.html -->
<!-- 在导航栏中添加 -->
{% if user.is_authenticated %}
    <li class="nav-item">
        <a class="nav-link" href="{% url 'user_activities' %}">我的活动</a>
    </li>
{% endif %}
```

## 总结

1. **文章点赞功能提供了一种简单的用户反馈机制**，让用户可以表达对内容的喜欢或支持，增强了用户参与度。

2. **文章收藏功能允许用户保存感兴趣的文章**，方便日后查看，提高了内容的可访问性和用户体验。

3. **文章分享功能提供了内容传播的渠道**，让用户可以将内容分享到社交媒体平台或通过其他方式分享给朋友，扩大了内容的影响力。

4. **用户活动记录功能跟踪用户的行为**，不仅可以为用户提供活动历史，还可以为系统提供用户行为数据，用于分析和改进。

5. **AJAX技术实现了无刷新交互**，提高了用户体验，让点赞、收藏等操作更加流畅。

6. **ManyToManyField实现了用户和文章的多对多关系**，一个用户可以点赞或收藏多篇文章，一篇文章也可以被多个用户点赞或收藏。

7. **Font Awesome提供了丰富的图标资源**，增强了界面的视觉效果，提高了用户体验。

8. **JavaScript增强了前端交互**，如链接复制功能、动态更新点赞和收藏状态等，提高了系统的易用性。

通过本节的学习，我们已经实现了博客系统的高级功能，包括文章点赞、收藏、分享等，进一步提升了系统的互动性和用户体验。至此，我们的博客系统已经具备了一个完整的内容平台所需的基本功能，可以满足用户的基本需求。

在实际开发中，还可以根据需求添加更多功能，如文章阅读量统计、热门文章推荐、用户关注、消息通知等，进一步提升系统的功能和用户体验。同时，也可以优化系统的性能和安全性，如添加缓存、防止CSRF攻击、XSS攻击等，确保系统的稳定和安全。