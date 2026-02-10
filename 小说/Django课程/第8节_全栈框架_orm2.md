# 第8节：全栈框架_orm2

## 来源

Django ORM的高级特性为开发者提供了强大的数据库操作能力，但同时也带来了性能优化的挑战。在实际应用中，我们需要深入理解ORM的工作原理，掌握查询优化技巧，合理使用缓存机制，以确保应用程序的性能和可扩展性。本节将深入探讨Django ORM的高级特性和性能优化策略，帮助开发者构建高效的数据库应用。

## 定义

### 查询优化

优化数据库查询的关键技术：

```python
from django.db.models import Prefetch
from django.core.cache import cache

# 使用select_related减少数据库查询
post = Post.objects.select_related('author', 'category').get(id=1)

# 使用prefetch_related处理多对多关系
posts = Post.objects.prefetch_related(
    Prefetch('tags', queryset=Tag.objects.only('name'))
).all()

# 使用only和defer选择性加载字段
users = User.objects.only('username', 'email').all()
posts = Post.objects.defer('content').all()
```

### 查询表达式和聚合

```python
from django.db.models import F, Q, Count, Avg, Max, Min
from django.db.models.functions import ExtractYear, Now

# 使用F表达式进行字段比较
Post.objects.filter(likes__gt=F('views') / 2)

# 复杂Q表达式查询
Post.objects.filter(
    Q(status='published') &
    (Q(author__username='admin') | Q(featured=True))
)

# 高级聚合查询
stats = Post.objects.values('category').annotate(
    post_count=Count('id'),
    avg_likes=Avg('likes'),
    max_views=Max('views'),
    min_views=Min('views')
)
```

### 原生SQL查询

```python
from django.db import connection

def get_popular_posts():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id, p.title, COUNT(c.id) as comment_count
            FROM blog_post p
            LEFT JOIN blog_comment c ON c.post_id = p.id
            WHERE p.status = 'published'
            GROUP BY p.id, p.title
            HAVING comment_count > 10
            ORDER BY comment_count DESC
            LIMIT 10
        """)
        return cursor.fetchall()
```

## 案例

### 缓存策略实现

```python
from django.core.cache import cache
from django.conf import settings
from django.utils.functional import cached_property

class CachedPost(models.Model):
    # ... 其他字段定义 ...
    
    @cached_property
    def comment_count(self):
        return self.comments.count()
    
    def get_cached_comments(self):
        cache_key = f'post_comments_{self.id}'
        comments = cache.get(cache_key)
        
        if comments is None:
            comments = list(self.comments.select_related('author').all())
            cache.set(cache_key, comments, timeout=3600)  # 缓存1小时
            
        return comments
    
    def clear_cache(self):
        cache_keys = [
            f'post_comments_{self.id}',
            f'post_tags_{self.id}',
        ]
        cache.delete_many(cache_keys)
```

### 批量操作优化

```python
from django.db import transaction
from django.db.models import F

def bulk_update_posts(posts_data):
    # 批量更新文章
    with transaction.atomic():
        # 创建批量更新列表
        posts_to_update = []
        for data in posts_data:
            post = Post(id=data['id'])
            post.title = data['title']
            post.content = data['content']
            posts_to_update.append(post)
        
        # 批量更新
        Post.objects.bulk_update(
            posts_to_update,
            ['title', 'content']
        )
        
        # 更新统计信息
        Post.objects.filter(
            id__in=[p.id for p in posts_to_update]
        ).update(update_count=F('update_count') + 1)

def bulk_create_comments(post, comments_data):
    # 批量创建评论
    comments = [
        Comment(
            post=post,
            author_id=data['author_id'],
            content=data['content']
        )
        for data in comments_data
    ]
    
    # 使用批量创建
    created_comments = Comment.objects.bulk_create(
        comments,
        batch_size=100  # 控制每批处理的数量
    )
    
    # 更新文章评论计数
    post.comment_count = F('comment_count') + len(created_comments)
    post.save(update_fields=['comment_count'])
```

### 查询优化实践

```python
class PostQuerySet(models.QuerySet):
    def optimized(self):
        return self.select_related('author', 'category')\
                   .prefetch_related('tags')\
                   .defer('content')
    
    def with_counts(self):
        return self.annotate(
            comment_count=Count('comments'),
            like_count=Count('likes')
        )
    
    def popular(self):
        return self.with_counts().filter(
            comment_count__gte=10,
            like_count__gte=20
        )

class Post(models.Model):
    # ... 字段定义 ...
    
    objects = PostQuerySet.as_manager()
    
    def save(self, *args, **kwargs):
        # 清除相关缓存
        cache_keys = [
            f'post_detail_{self.id}',
            'post_list_page_1',
            f'category_posts_{self.category_id}'
        ]
        cache.delete_many(cache_keys)
        
        super().save(*args, **kwargs)

def get_category_posts(category_id, page=1):
    cache_key = f'category_posts_{category_id}_page_{page}'
    posts = cache.get(cache_key)
    
    if posts is None:
        posts = Post.objects.optimized()\
            .filter(category_id=category_id)\
            .with_counts()\
            .order_by('-created_at')
        
        paginator = Paginator(posts, 20)
        posts = paginator.get_page(page)
        
        cache.set(cache_key, posts, timeout=3600)
    
    return posts
```

## 总结

1. **查询优化是提升性能的关键**，合理使用select_related和prefetch_related可以显著减少数据库查询次数。

2. **缓存策略对性能影响重大**，需要根据业务场景选择适当的缓存粒度和失效策略。

3. **批量操作可以提高数据处理效率**，但需要注意内存使用和事务管理。

4. **合理使用查询表达式和聚合函数**可以减少代码复杂度，提高查询效率。

5. **原生SQL在特定场景下是必要的**，但应该谨慎使用，确保SQL语句的安全性和可维护性。

6. **模型管理器和QuerySet方法**可以封装常用的查询逻辑，提高代码复用性。

7. **数据库索引设计**对查询性能有重要影响，需要根据查询模式合理创建索引。

8. **性能优化是一个持续的过程**，需要通过监控和分析不断改进查询策略。