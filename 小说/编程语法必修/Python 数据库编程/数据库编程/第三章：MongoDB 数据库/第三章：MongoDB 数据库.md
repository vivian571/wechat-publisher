# 第三章：MongoDB 数据库——文档存储的"百变大师"

嘿，小伙伴们！上次我们聊了 Redis 这个"闪电侠"，今天咱们来认识另一位超级英雄——**<font color='red'>MongoDB</font>**！

你是不是经常遇到这种情况：数据结构变来变去，关系型数据库改起来太麻烦？或者需要存储复杂的嵌套数据，但 SQL 表格太死板？

这时候，**<font color='blue'>MongoDB 就是你的救星！</font>**

## 学习目标

学完本章，你将能够：

1. 理解 MongoDB 的基本概念和应用场景
2. 掌握 MongoDB 数据库和集合的基本操作
3. 熟练使用 MongoDB 的 CRUD（增删改查）操作
4. 使用 Python 的 PyMongo 库连接并操作 MongoDB
5. 理解并应用 MongoDB 的高级特性（索引、聚合、备份恢复）

准备好了吗？Let's Go！

## 一、MongoDB 简介——不一样的数据库

**<font color='purple'>MongoDB 是什么？简单说就是一个存储 JSON 文档的数据库！</font>**

传统数据库（如 MySQL）把数据存在表格里，而 MongoDB 把数据存在"文档"里（类似 JSON 对象）。

这种设计有什么好处？

1. **<font color='green'>灵活的数据模型</font>**：不需要预先定义表结构，想存啥存啥
2. **<font color='orange'>层次化数据存储</font>**：可以嵌套存储复杂数据，比如数组、对象
3. **<font color='blue'>高性能</font>**：针对文档的存取进行了优化，查询速度飞快
4. **<font color='red'>高可用性</font>**：支持复制集和分片，可以横向扩展

**<font color='purple'>MongoDB 适合什么场景？</font>**

1. 需要灵活数据模型的应用（如内容管理系统）
2. 大数据量、高并发的应用（如日志系统、社交网络）
3. 需要快速迭代开发的项目（不用每次修改都调整表结构）
4. 存储半结构化或非结构化数据（如用户行为分析）

## 二、MongoDB 基础操作——入门必备

### 1. 数据库操作

**<font color='green'>查看当前数据库：</font>**

```bash
# 显示当前所在的数据库
db
```

**<font color='blue'>查看所有数据库：</font>**

```bash
# 显示所有数据库列表
show dbs
```

**<font color='orange'>切换/创建数据库：</font>**

```bash
# 切换到 mydb 数据库（如果不存在则创建）
use mydb
```

**<font color='red'>删除数据库：</font>**

```bash
# 删除当前数据库
db.dropDatabase()
```

**<font color='purple'>小技巧：</font>** MongoDB 中，数据库在真正插入数据前是不会被创建的，即使你执行了 `use` 命令。

### 2. 集合操作

在 MongoDB 中，"集合"就相当于关系型数据库中的"表"。

**<font color='green'>创建集合：</font>**

```bash
# 显式创建集合
db.createCollection("users")

# 隐式创建集合（插入数据时自动创建）
db.users.insert({name: "小明", age: 18})
```

**<font color='blue'>查看集合：</font>**

```bash
# 显示当前数据库中的所有集合
show collections
```

**<font color='red'>删除集合：</font>**

```bash
# 删除 users 集合
db.users.drop()
```

## 三、MongoDB 数据类型——百宝箱

**<font color='purple'>MongoDB 支持多种数据类型，比 JSON 更丰富：</font>**

1. **字符串（String）**：UTF-8 编码的文本
2. **整数（Integer）**：32 位或 64 位整数
3. **浮点数（Double）**：64 位浮点数
4. **布尔值（Boolean）**：true 或 false
5. **日期（Date）**：存储日期和时间
6. **对象 ID（ObjectId）**：12 字节的唯一标识符，常用作主键
7. **数组（Array）**：值的列表或集合
8. **嵌入式文档（Embedded Document）**：文档中嵌套的文档
9. **二进制数据（Binary Data）**：存储二进制信息，如图片
10. **正则表达式（Regular Expression）**：用于模式匹配

**<font color='green'>最常用的是 ObjectId，它是 MongoDB 自动生成的唯一标识符：</font>**

```bash
# ObjectId 由 12 字节组成：
# - 4 字节：时间戳
# - 3 字节：机器标识符
# - 2 字节：进程 ID
# - 3 字节：计数器
```

这意味着 ObjectId 基本上是唯一的，而且包含创建时间信息！

## 四、MongoDB 数据操作——CRUD 大法

### 1. 插入操作（Create）

**<font color='blue'>插入单个文档：</font>**

```bash
# 插入一个用户文档
db.users.insertOne(
  {
    name: "张三",
    age: 25,
    email: "zhangsan@example.com",
    hobbies: ["读书", "游泳"],
    address: {
      city: "北京",
      district: "朝阳区"
    }
  }
)
```

**<font color='green'>插入多个文档：</font>**

```bash
# 批量插入用户文档
db.users.insertMany([
  {
    name: "李四",
    age: 30,
    email: "lisi@example.com"
  },
  {
    name: "王五",
    age: 22,
    email: "wangwu@example.com"
  }
])
```

**<font color='red'>小技巧：</font>** 如果不指定 `_id` 字段，MongoDB 会自动生成一个 ObjectId 作为主键。

### 2. 查询操作（Read）

**<font color='purple'>查询所有文档：</font>**

```bash
# 查询 users 集合中的所有文档
db.users.find()

# 格式化显示结果
db.users.find().pretty()
```

**<font color='orange'>条件查询：</font>**

```bash
# 查询年龄为 25 的用户
db.users.find({age: 25})

# 查询年龄大于 20 的用户
db.users.find({age: {$gt: 20}})

# 查询年龄在 20 到 30 之间的用户
db.users.find({age: {$gte: 20, $lte: 30}})

# 查询名字为张三或李四的用户
db.users.find({name: {$in: ["张三", "李四"]}})

# 查询住在北京的用户（嵌套文档查询）
db.users.find({"address.city": "北京"})

# 查询喜欢游泳的用户（数组查询）
db.users.find({hobbies: "游泳"})
```

**<font color='blue'>投影查询（只返回特定字段）：</font>**

```bash
# 只返回用户的姓名和邮箱
db.users.find({}, {name: 1, email: 1, _id: 0})
```

**<font color='green'>排序、限制和跳过：</font>**

```bash
# 按年龄升序排序
db.users.find().sort({age: 1})

# 按年龄降序排序
db.users.find().sort({age: -1})

# 限制返回 5 条记录
db.users.find().limit(5)

# 跳过前 5 条记录
db.users.find().skip(5)

# 分页查询：每页 10 条，查询第 2 页
db.users.find().skip(10).limit(10)
```

### 3. 更新操作（Update）

**<font color='red'>更新单个文档：</font>**

```bash
# 更新张三的年龄为 26
db.users.updateOne(
  {name: "张三"},
  {$set: {age: 26}}
)
```

**<font color='purple'>更新多个文档：</font>**

```bash
# 将所有年龄小于 20 的用户年龄增加 1
db.users.updateMany(
  {age: {$lt: 20}},
  {$inc: {age: 1}}
)
```

**<font color='orange'>更新操作符：</font>**

```bash
# $set：设置字段值
db.users.updateOne({name: "张三"}, {$set: {email: "zhangsan_new@example.com"}})

# $inc：增加字段值
db.users.updateOne({name: "张三"}, {$inc: {age: 2}})

# $push：向数组添加元素
db.users.updateOne({name: "张三"}, {$push: {hobbies: "篮球"}})

# $pull：从数组移除元素
db.users.updateOne({name: "张三"}, {$pull: {hobbies: "游泳"}})

# $unset：删除字段
db.users.updateOne({name: "张三"}, {$unset: {email: ""}})
```

### 4. 删除操作（Delete）

**<font color='blue'>删除单个文档：</font>**

```bash
# 删除名为张三的用户
db.users.deleteOne({name: "张三"})
```

**<font color='green'>删除多个文档：</font>**

```bash
# 删除年龄大于 30 的所有用户
db.users.deleteMany({age: {$gt: 30}})
```

**<font color='red'>删除所有文档：</font>**

```bash
# 清空集合（但保留集合及其索引）
db.users.deleteMany({})
```

## 五、MongoDB 高级特性——进阶技能

### 1. 索引操作

**<font color='purple'>索引就像书的目录，能让查询飞起来：</font>**

```bash
# 创建单字段索引
db.users.createIndex({name: 1})  # 1 表示升序索引，-1 表示降序索引

# 创建复合索引
db.users.createIndex({age: 1, name: 1})

# 创建唯一索引
db.users.createIndex({email: 1}, {unique: true})

# 创建文本索引（全文搜索）
db.articles.createIndex({content: "text"})

# 查看集合的所有索引
db.users.getIndexes()

# 删除特定索引
db.users.dropIndex("name_1")

# 删除所有索引
db.users.dropIndexes()
```

### 2. 聚合操作

**<font color='orange'>聚合管道可以对数据进行复杂处理：</font>**

```bash
# 计算每个城市的用户数量
db.users.aggregate([
  {$group: {_id: "$address.city", count: {$sum: 1}}}
])

# 计算每个年龄段的用户数量
db.users.aggregate([
  {$bucket: {
    groupBy: "$age",
    boundaries: [0, 18, 30, 50, 100],
    default: "其他",
    output: {count: {$sum: 1}}
  }}
])

# 计算用户的平均年龄
db.users.aggregate([
  {$group: {_id: null, avgAge: {$avg: "$age"}}}
])

# 查找并显示每个城市年龄最大的用户
db.users.aggregate([
  {$sort: {age: -1}},
  {$group: {_id: "$address.city", oldestUser: {$first: "$$ROOT"}}},
  {$project: {_id: 1, name: "$oldestUser.name", age: "$oldestUser.age"}}
])
```

### 3. 数据备份与恢复

**<font color='blue'>备份数据库：</font>**

```bash
# 备份整个数据库
mongodump --db mydb --out /backup/path

# 备份特定集合
mongodump --db mydb --collection users --out /backup/path
```

**<font color='green'>恢复数据库：</font>**

```bash
# 恢复整个数据库
mongorestore --db mydb /backup/path/mydb

# 恢复特定集合
mongorestore --db mydb --collection users /backup/path/mydb/users.bson
```

## 六、PyMongo：Python 操作 MongoDB

### 1. 安装与连接

```python
# 安装 PyMongo
# pip install pymongo

# 导入 PyMongo
import pymongo
from pymongo import MongoClient

# 连接 MongoDB 服务器
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库
db = client['mydb']

# 选择集合
users = db['users']
```

### 2. 插入操作

```python
# 插入单个文档
user = {
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com",
    "hobbies": ["读书", "游泳"],
    "address": {
        "city": "北京",
        "district": "朝阳区"
    }
}
result = users.insert_one(user)
print(f"插入的文档ID: {result.inserted_id}")

# 插入多个文档
user_list = [
    {"name": "李四", "age": 30, "email": "lisi@example.com"},
    {"name": "王五", "age": 22, "email": "wangwu@example.com"}
]
result = users.insert_many(user_list)
print(f"插入的文档ID列表: {result.inserted_ids}")
```

### 3. 查询操作

```python
# 查询单个文档
user = users.find_one({"name": "张三"})
print(user)

# 查询多个文档
for user in users.find({"age": {"$gt": 20}}):
    print(user)

# 条件查询
query = {"age": {"$gte": 20, "$lte": 30}}
for user in users.find(query):
    print(f"{user['name']} - {user['age']}岁")

# 投影查询（只返回特定字段）
for user in users.find({}, {"name": 1, "email": 1, "_id": 0}):
    print(f"{user['name']} - {user['email']}")

# 排序
for user in users.find().sort("age", pymongo.ASCENDING):
    print(f"{user['name']} - {user['age']}岁")

# 限制结果数量
for user in users.find().limit(5):
    print(user['name'])
```

### 4. 更新操作

```python
# 更新单个文档
result = users.update_one(
    {"name": "张三"},
    {"$set": {"age": 26}}
)
print(f"匹配的文档数: {result.matched_count}")
print(f"修改的文档数: {result.modified_count}")

# 更新多个文档
result = users.update_many(
    {"age": {"$lt": 20}},
    {"$inc": {"age": 1}}
)
print(f"修改的文档数: {result.modified_count}")

# 使用不同的更新操作符
users.update_one(
    {"name": "张三"},
    {"$push": {"hobbies": "篮球"}}
)
```

### 5. 删除操作

```python
# 删除单个文档
result = users.delete_one({"name": "张三"})
print(f"删除的文档数: {result.deleted_count}")

# 删除多个文档
result = users.delete_many({"age": {"$gt": 30}})
print(f"删除的文档数: {result.deleted_count}")
```

### 6. 聚合操作

```python
# 计算每个城市的用户数量
pipeline = [
    {"$group": {"_id": "$address.city", "count": {"$sum": 1}}}
]
for result in users.aggregate(pipeline):
    print(f"{result['_id']}: {result['count']}人")

# 计算用户的平均年龄
pipeline = [
    {"$group": {"_id": None, "avgAge": {"$avg": "$age"}}}
]
result = list(users.aggregate(pipeline))[0]
print(f"平均年龄: {result['avgAge']:.1f}岁")
```

## 应用场景

**<font color='green'>MongoDB 在实际项目中有这些超赞的应用：</font>**

1. **内容管理系统**：存储文章、评论、用户信息等
2. **日志系统**：收集和分析应用程序日志
3. **电商平台**：存储商品信息、用户购物车、订单等
4. **社交网络**：存储用户资料、关系网络、动态等
5. **物联网应用**：处理传感器数据
6. **实时分析**：结合聚合框架进行数据分析
7. **地理位置服务**：使用地理空间索引实现附近的人、店铺等功能

## 实战案例：简易博客系统

让我们用 PyMongo 实现一个简单的博客系统：

```python
from pymongo import MongoClient
from datetime import datetime
import pprint

# 连接数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['blog_system']

# 创建集合
users = db['users']
articles = db['articles']
comments = db['comments']

# 添加用户
def add_user(username, email, password):
    user = {
        "username": username,
        "email": email,
        "password": password,  # 实际应用中应该加密存储
        "created_at": datetime.now()
    }
    return users.insert_one(user).inserted_id

# 发布文章
def publish_article(title, content, author_id):
    article = {
        "title": title,
        "content": content,
        "author_id": author_id,
        "created_at": datetime.now(),
        "tags": [],
        "likes": 0
    }
    return articles.insert_one(article).inserted_id

# 添加评论
def add_comment(article_id, user_id, content):
    comment = {
        "article_id": article_id,
        "user_id": user_id,
        "content": content,
        "created_at": datetime.now()
    }
    return comments.insert_one(comment).inserted_id

# 获取文章及其评论
def get_article_with_comments(article_id):
    # 获取文章
    article = articles.find_one({"_id": article_id})
    if not article:
        return None
    
    # 获取作者信息
    author = users.find_one({"_id": article["author_id"]})
    article["author"] = {"username": author["username"], "email": author["email"]}
    
    # 获取评论
    article_comments = []
    for comment in comments.find({"article_id": article_id}).sort("created_at", 1):
        # 获取评论者信息
        commenter = users.find_one({"_id": comment["user_id"]})
        comment["user"] = {"username": commenter["username"]}
        article_comments.append(comment)
    
    article["comments"] = article_comments
    return article

# 示例使用
if __name__ == "__main__":
    # 清空集合
    users.delete_many({})
    articles.delete_many({})
    comments.delete_many({})
    
    # 添加用户
    user1_id = add_user("张三", "zhangsan@example.com", "password123")
    user2_id = add_user("李四", "lisi@example.com", "password456")
    
    # 发布文章
    article_id = publish_article(
        "MongoDB 入门指南",
        "MongoDB 是一个基于分布式文件存储的文档型数据库...",
        user1_id
    )
    
    # 添加评论
    add_comment(article_id, user2_id, "写得真好，学习了！")
    add_comment(article_id, user1_id, "谢谢支持！")
    
    # 获取文章及评论
    article_with_comments = get_article_with_comments(article_id)
    pprint.pprint(article_with_comments)
```

## 总结

**<font color='red'>MongoDB 就像数据世界的"百变大师"：</font>**

1. **灵活多变**：没有固定模式，数据结构可以随时调整
2. **性能强劲**：基于文档的存储方式，读写性能出色
3. **扩展性好**：可以轻松应对数据量增长
4. **查询强大**：支持丰富的查询语法和聚合操作
5. **开发友好**：JSON 式的文档格式，对开发者非常友好

掌握了 MongoDB，你就拥有了一把处理非结构化和半结构化数据的"瑞士军刀"！

**<font color='blue'>小作业：</font>** 尝试用 MongoDB 和 PyMongo 实现一个简单的待办事项应用，包括添加任务、标记完成、按标签分类等功能。

下一章，我们将探索更多数据库的奥秘，敬请期待！