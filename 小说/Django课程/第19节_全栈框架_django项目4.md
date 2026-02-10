# 第19节：全栈框架_django项目4

## 来源

在前三节中，我们已经完成了博客系统的基本框架搭建，实现了用户认证、文章发布、编辑、删除等功能。本节将继续开发这个博客系统，重点实现评论功能，让用户能够在文章下方发表评论，增强系统的互动性。评论功能是社交媒体和内容平台的核心组成部分，它促进了用户之间的交流和互动，提高了平台的活跃度和用户粘性。

## 定义

### 评论系统

评论系统是允许用户对内容（如文章、图片、视频等）发表意见和看法的功能模块。在博客系统中，评论系统通常包括评论的创建、显示、管理等功能，有时还包括回复、点赞、举报等高级特性。

### 评论模型

评论模型是存储评论数据的数据库模型，通常包括评论内容、评论者、评论时间、关联的文章等字段。在Django中，评论模型通常通过外键与文章模型和用户模型关联。

### 嵌套评论

嵌套评论（或回复功能）允许用户回复特定的评论，形成评论树结构。这种结构可以更清晰地展示用户之间的对话关系，提高评论区的交互性。

## 案例

### 1. 创建评论模型

首先，我们需要创建一个评论模型来存储评论数据：

```python
# blog/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    # 现有的Post模型代码...

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-date_posted']
    
    def __str__(self):
        return f'评论 by {self.author.username} on {self.post.title}'
```

注意，我们添加了一个`parent`字段，用于实现嵌套评论功能。如果`parent`为`None`，则表示这是一个顶级评论；否则，它是对另一个评论的回复。

### 2. 创建评论表单

接下来，我们需要创建一个表单来处理评论的提交：

```python
# blog/forms.py
from django import forms
from .models import Post, Comment

class PostForm(models.ModelForm):
    # 现有的PostForm代码...

class CommentForm(forms.ModelForm):
    content = forms.CharField(label='评论', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': '发表你的评论...',
        'rows': 4
    }))
    
    class Meta:
        model = Comment
        fields = ['content']
```

### 3. 更新文章详情视图

我们需要更新文章详情视图，以处理评论的提交和显示：

```python
# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).order_by('-date_posted')  # 只获取顶级评论
    
    if request.method == 'POST':
        # 检查用户是否登录
        if not request.user.is_authenticated:
            messages.error(request, '请先登录后再发表评论！')
            return redirect('login')
        
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            
            # 检查是否是回复
            reply_id = request.POST.get('reply_id')
            if reply_id:
                parent_comment = get_object_or_404(Comment, id=reply_id)
                new_comment.parent = parent_comment
            
            new_comment.save()
            messages.success(request, '评论已成功发布！')
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    }
    return render(request, 'blog/post_detail.html', context)
```

### 4. 更新文章详情模板

现在，我们需要更新文章详情模板，添加评论区和评论表单：

```html
<!-- templates/blog/post_detail.html -->
{% extends 'base.html' %}

{% block title %}{{ post.title }} - 博客系统{% endblock %}

{% block content %}
    <!-- 文章内容卡片 -->
    <div class="card mb-4">
        <div class="card-header">
            <h2 class="card-title">{{ post.title }}</h2>
            <small class="text-muted">由 <a href="{% url 'user_posts' post.author.username %}">{{ post.author.username }}</a> 发布于 {{ post.date_posted|date:"Y-m-d H:i" }}</small>
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
    
    <!-- 评论表单 -->
    <div class="card mb-4">
        <div class="card-header">
            <h3>发表评论</h3>
        </div>
        <div class="card-body">
            {% if user.is_authenticated %}
                <form method="POST" id="comment-form">
                    {% csrf_token %}
                    <input type="hidden" name="reply_id" id="reply-id" value="">
                    <div class="form-group">
                        {{ comment_form.content }}
                        {% if comment_form.content.errors %}
                            <div class="text-danger">
                                {% for error in comment_form.content.errors %}
                                    {{ error }}
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn btn-primary">提交评论</button>
                        <button type="button" id="cancel-reply" class="btn btn-secondary d-none">取消回复</button>
                    </div>
                </form>
            {% else %}
                <p>请 <a href="{% url 'login' %}">登录</a> 后发表评论。</p>
            {% endif %}
        </div>
    </div>
    
    <!-- 评论列表 -->
    <div class="card mb-4">
        <div class="card-header">
            <h3>评论 ({{ comments.count }})</h3>
        </div>
        <div class="card-body">
            {% if comments %}
                {% for comment in comments %}
                    <div class="media mb-4">
                        <img class="d-flex mr-3 rounded-circle" src="{{ comment.author.profile.image.url }}" alt="" width="50" height="50">
                        <div class="media-body">
                            <h5 class="mt-0">{{ comment.author.username }} <small class="text-muted">{{ comment.date_posted|date:"Y-m-d H:i" }}</small></h5>
                            <p>{{ comment.content|linebreaks }}</p>
                            {% if user.is_authenticated %}
                                <button class="btn btn-sm btn-link reply-btn" data-comment-id="{{ comment.id }}">回复</button>
                            {% endif %}
                            
                            <!-- 嵌套评论 -->
                            {% for reply in comment.replies.all %}
                                <div class="media mt-3">
                                    <img class="d-flex mr-3 rounded-circle" src="{{ reply.author.profile.image.url }}" alt="" width="40" height="40">
                                    <div class="media-body">
                                        <h5 class="mt-0">{{ reply.author.username }} <small class="text-muted">{{ reply.date_posted|date:"Y-m-d H:i" }}</small></h5>
                                        <p>{{ reply.content|linebreaks }}</p>
                                        {% if user.is_authenticated %}
                                            <button class="btn btn-sm btn-link reply-btn" data-comment-id="{{ comment.id }}">回复</button>
                                        {% endif %}
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p>暂无评论，成为第一个评论的人吧！</p>
            {% endif %}
        </div>
    </div>
{% endblock %}

{% block extra_js %}
<script>
    // 处理回复功能的JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        const replyButtons = document.querySelectorAll('.reply-btn');
        const commentForm = document.getElementById('comment-form');
        const replyIdInput = document.getElementById('reply-id');
        const cancelReplyButton = document.getElementById('cancel-reply');
        
        replyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const commentId = this.getAttribute('data-comment-id');
                replyIdInput.value = commentId;
                commentForm.scrollIntoView({ behavior: 'smooth' });
                cancelReplyButton.classList.remove('d-none');
            });
        });
        
        cancelReplyButton.addEventListener('click', function() {
            replyIdInput.value = '';
            this.classList.add('d-none');
        });
    });
</script>
{% endblock %}
```

### 5. 更新基础模板

为了支持额外的JavaScript代码，我们需要更新基础模板：

```html
<!-- templates/base.html -->
<!-- 在页面底部添加 -->
{% block extra_js %}{% endblock %}
```

### 6. 运行迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. 添加评论管理功能

为了让管理员能够管理评论，我们可以在admin.py中注册评论模型：

```python
# blog/admin.py
from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'date_posted', 'content')
    list_filter = ('date_posted', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    date_hierarchy = 'date_posted'
```

### 8. 添加评论删除功能

让用户能够删除自己的评论：

```python
# blog/views.py
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    # 检查当前用户是否是评论作者
    if comment.author != request.user:
        messages.error(request, '您没有权限删除这条评论！')
        return redirect('post_detail', pk=post_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, '评论已成功删除！')
        return redirect('post_detail', pk=post_pk)
    
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})
```

更新URL配置：

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有的URL配置...
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]
```

创建评论删除确认模板：

```html
<!-- templates/blog/comment_confirm_delete.html -->
{% extends 'base.html' %}

{% block title %}删除评论 - 博客系统{% endblock %}

{% block content %}
    <div class="card">
        <div class="card-header">
            <h2>删除评论</h2>
        </div>
        <div class="card-body">
            <form method="POST">
                {% csrf_token %}
                <fieldset class="form-group">
                    <p>您确定要删除这条评论吗？此操作不可撤销！</p>
                    <div class="alert alert-secondary">
                        <p>{{ comment.content }}</p>
                    </div>
                </fieldset>
                <div class="form-group">
                    <button class="btn btn-danger" type="submit">确认删除</button>
                    <a class="btn btn-secondary" href="{% url 'post_detail' comment.post.pk %}">取消</a>
                </div>
            </form>
        </div>
    </div>
{% endblock %}
```

更新评论模板，添加删除按钮：

```html
<!-- templates/blog/post_detail.html -->
<!-- 在评论和回复的操作区添加 -->
{% if user == comment.author %}
    <a href="{% url 'comment_delete' comment.id %}" class="btn btn-sm btn-danger">删除</a>
{% endif %}

<!-- 在回复的操作区也添加类似的代码 -->
{% if user == reply.author %}
    <a href="{% url 'comment_delete' reply.id %}" class="btn btn-sm btn-danger">删除</a>
{% endif %}
```

## 总结

1. **评论功能是社交媒体和内容平台的核心组成部分**，它促进了用户之间的交流和互动，提高了平台的活跃度和用户粘性。

2. **评论模型通常通过外键与文章模型和用户模型关联**，存储评论内容、评论者、评论时间等信息。

3. **嵌套评论功能允许用户回复特定的评论**，形成评论树结构，提高评论区的交互性。

4. **评论表单处理用户提交的评论内容**，并进行必要的验证和处理。

5. **评论管理功能允许管理员和用户管理评论**，包括删除不当评论等操作。

6. **JavaScript可以增强评论功能的交互性**，如实现回复功能、动态加载评论等。

7. **权限控制确保只有评论作者才能删除评论**，保护用户的权益和系统的安全。

8. **消息框架提供了一种向用户显示通知的方式**，如评论成功、删除成功等提示，提高了用户体验。

通过本节的学习，我们已经实现了博客系统的评论功能，包括评论的创建、显示、回复和删除等。在下一节中，我们将继续开发这个博客系统，添加搜索功能和标签功能，让用户能够更方便地查找和分类文章。