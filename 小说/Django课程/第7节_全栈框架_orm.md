# 第7节：全栈框架_orm

## 来源

Django的ORM（Object-Relational Mapping）是一个强大的数据库抽象层，它将数据库表映射为Python类，将数据库操作转换为Python方法调用。这种抽象使得开发者可以用面向对象的方式来处理数据库，而不需要直接编写SQL语句。ORM不仅简化了数据库操作，还提供了数据库无关性，使得应用程序可以轻松地在不同数据库系统之间迁移。

## 定义

### 模型定义

模型类继承自django.db.models.Model，使用字段类定义数据结构：

```python
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='publish_date')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        ordering = ['-publish_date']
        
    def __str__(self):
        return self.title
```

### 查询操作

Django ORM提供了丰富的查询API：

```python
# 基本查询
Post.objects.all()  # 获取所有文章
Post.objects.filter(status='published')  # 过滤已发布文章
Post.objects.exclude(status='draft')  # 排除草稿

# 关联查询
Post.objects.select_related('author', 'category').all()  # 预加载关联对象
Category.objects.prefetch_related('post_set').all()  # 预加载反向关联

# 聚合和注解
from django.db.models import Count, Avg
Category.objects.annotate(post_count=Count('post'))
Post.objects.values('category').annotate(avg_posts=Count('id'))
```

### 模型关系

Django支持多种模型关系：

```python
# 一对多关系
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# 多对多关系
class Tag(models.Model):
    name = models.CharField(max_length=50)
    posts = models.ManyToManyField(Post, related_name='tags')

# 一对一关系
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/')
```

## 案例

### 高级查询

```python
from django.db.models import Q, F, Count
from django.utils import timezone

def get_trending_posts(days=7):
    # 获取最近7天的热门文章
    recent_date = timezone.now() - timezone.timedelta(days=days)
    
    return Post.objects.filter(
        publish_date__gte=recent_date,
        status='published'
    ).annotate(
        comment_count=Count('comment'),
        # 使用F表达式进行字段比较
    ).filter(
        comment_count__gte=F('views') / 10  # 评论数超过浏览量的10%
    ).order_by('-comment_count')

def search_posts(query):
    # 复杂查询条件
    return Post.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(author__username__icontains=query)
    ).distinct()
```

### 批量操作

```python
from django.db import transaction

def bulk_publish_posts(category_id):
    # 批量发布某个分类下的所有草稿
    with transaction.atomic():
        posts = Post.objects.filter(
            category_id=category_id,
            status='draft'
        )
        
        # 批量更新
        posts.update(status='published')
        
        # 创建发布记录
        publish_records = [
            PublishRecord(post=post, publisher=request.user)
            for post in posts
        ]
        PublishRecord.objects.bulk_create(publish_records)

def transfer_posts(old_category, new_category):
    # 转移文章分类
    Post.objects.filter(category=old_category).update(category=new_category)
```

### 自定义管理器

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
    
    def popular(self):
        return self.get_queryset().annotate(
            comment_count=Count('comment')
        ).order_by('-comment_count')

class Post(models.Model):
    # ...
    objects = models.Manager()
    published = PublishedManager()
    
    @property
    def is_recent(self):
        return timezone.now() - self.publish_date <= timezone.timedelta(days=7)
    
    def get_related_posts(self):
        return Post.published.filter(
            tags__in=self.tags.all()
        ).exclude(id=self.id).distinct()
```

## 总结

1. **Django ORM提供了高层次的数据库抽象**，使得开发者可以用Python代码操作数据库，提高开发效率。

2. **模型定义清晰直观**，通过类和字段定义数据结构，支持丰富的字段类型和约束。

3. **查询API功能强大**，支持复杂的查询条件、关联查询、聚合操作等。

4. **支持多种数据库关系**，包括一对一、一对多、多对多关系，满足复杂的数据建模需求。

5. **提供事务支持和批量操作**，确保数据一致性和操作效率。

6. **自定义管理器机制**允许封装常用的查询逻辑，提高代码复用性。

7. **Meta类配置**提供了丰富的模型元数据选项，如排序、索引、权限等。

8. **数据库无关性**使得应用程序可以在不同数据库系统之间迁移，提高了可移植性。