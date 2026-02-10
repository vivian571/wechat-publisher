# 第二章：Redis 数据库——数据存储的"闪电侠"

嘿，小伙伴们！上次我们聊了 MySQL 这个"老大哥"，今天咱们来认识另一位超级英雄——**<font color='red'>Redis</font>**！

你是不是经常遇到这种情况：网站访问量突然暴增，数据库被打得喘不过气来？或者需要临时存储一些数据，但又不想大动干戈去修改数据库结构？

这时候，**<font color='blue'>Redis 就是你的救星！</font>**

## 学习目标

学完本章，你将能够：

1. 熟练操作 Redis 服务端和客户端的基本命令
2. 掌握 Redis 五大数据类型（string、hash、list、set、zset）的操作
3. 使用 Python 代码连接并操作 Redis 数据库
4. 理解并应用 Redis 事务、管道和发布订阅模式

准备好了吗？Let's Go！

## 一、Redis 服务端和客户端基本操作命令

### 1. 服务端启动停止命令

**<font color='green'>启动 Redis 服务器超简单：</font>**

```bash
# Windows 下启动 Redis 服务器
redis-server.exe

# Linux/Mac 下启动 Redis 服务器
redis-server

# 指定配置文件启动
redis-server /path/to/redis.conf
```

**<font color='orange'>停止 Redis 服务也很轻松：</font>**

```bash
# 在 Redis 客户端中优雅关闭
shutdown

# 或者直接关闭进程（不推荐）
```

### 2. 客户端连接命令

连接 Redis 服务器就像给好友打电话一样简单：

```bash
# 连接本地 Redis 服务器
redis-cli

# 连接指定主机和端口的 Redis 服务器
redis-cli -h 127.0.0.1 -p 6379

# 连接并验证密码
redis-cli -a yourpassword
```

### 3. 查看 Redis 信息命令

想知道 Redis 的小秘密？试试这些命令：

```bash
# 查看 Redis 版本
info server

# 查看 Redis 统计信息
info stats

# 查看所有配置
config get *

# 查看特定配置
config get maxmemory
```

## 二、Redis 数据操作

**<font color='purple'>Redis 有五种基本数据类型，就像五种超能力！</font>**

### 1. String 类型操作

String 是 Redis 最基础的数据类型，就像超级英雄的基本功。

```bash
# 设置字符串值
SET name "小明"

# 获取字符串值
GET name  # 返回 "小明"

# 追加字符串
APPEND name "是个好同学"  # 现在 name 的值是 "小明是个好同学"

# 获取字符串长度
STRLEN name  # 返回 7（中文字符在 UTF-8 中占 3 个字节）
```

**<font color='red'>小技巧：</font>** String 类型不仅可以存文本，还能存数字、二进制数据，甚至是序列化的对象！

### 2. 键命令操作

管理 Redis 中的键就像整理你的钥匙串：

```bash
# 查看所有键
KEYS *

# 查看特定模式的键
KEYS user:*

# 判断键是否存在
EXISTS name  # 如果存在返回 1，不存在返回 0

# 删除键
DEL name

# 设置过期时间（秒）
EXPIRE session:123 300  # 设置 session:123 在 300 秒后过期
```

**<font color='blue'>过期时间太实用了！</font>** 特别适合存储验证码、会话信息等临时数据。

### 3. Hash 类型操作

Hash 类型就像小型数据库，存储对象超方便：

```bash
# 设置哈希字段值
HSET user:1 name "张三" age 25 city "北京"

# 获取哈希字段值
HGET user:1 name  # 返回 "张三"

# 获取所有哈希字段和值
HGETALL user:1

# 删除哈希字段
HDEL user:1 city
```

**<font color='green'>Hash 特别适合存储用户信息、商品信息等结构化数据！</font>**

### 4. List 类型操作

List 类型就像一个双向队列，两头都能操作：

```bash
# 向列表左侧插入元素
LPUSH messages "最新消息"

# 向列表右侧插入元素
RPUSH messages "较早消息"

# 从列表左侧弹出元素
LPOP messages

# 从列表右侧弹出元素
RPOP messages

# 获取列表指定范围元素
LRANGE messages 0 -1  # 获取所有元素，0 是起始索引，-1 表示最后一个元素
```

**<font color='orange'>List 超适合做消息队列、最新动态、排行榜等场景！</font>**

### 5. Set 类型操作

Set 类型就像朋友圈，不重复、无序：

```bash
# 向集合添加元素
SADD friends "小明" "小红" "小刚"

# 判断元素是否在集合中
SISMEMBER friends "小明"  # 存在返回 1，不存在返回 0

# 获取集合所有元素
SMEMBERS friends

# 集合间的操作
SADD group1 "A" "B" "C"
SADD group2 "B" "C" "D"
SINTER group1 group2  # 交集："B", "C"
SUNION group1 group2  # 并集："A", "B", "C", "D"
SDIFF group1 group2   # 差集："A"
```

**<font color='purple'>Set 特别适合标签系统、共同好友、抽奖等场景！</font>**

### 6. ZSet 类型操作

ZSet（有序集合）就像带分数的排行榜：

```bash
# 向有序集合添加元素
ZADD scores 89 "小明" 92 "小红" 76 "小刚"

# 获取有序集合指定范围元素
ZRANGE scores 0 -1  # 从低到高获取所有元素
ZREVRANGE scores 0 -1  # 从高到低获取所有元素

# 获取元素的分数
ZSCORE scores "小红"  # 返回 92

# 根据分数范围获取元素
ZRANGEBYSCORE scores 80 100  # 获取 80-100 分的学生
```

**<font color='red'>ZSet 简直就是排行榜、权重队列的完美选择！</font>**

## 三、Python 操作 Redis

光会命令行操作怎么够？让我们用 Python 来驾驭 Redis！

### 1. Redis 库安装与导入

```python
# 安装 Redis 库
# pip install redis

# 导入 Redis 库
import redis

# 连接 Redis 服务器
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
```

**<font color='blue'>参数说明：</font>**
- `host`：Redis 服务器地址
- `port`：Redis 服务器端口
- `db`：使用的数据库编号
- `decode_responses`：自动将字节解码为字符串

### 2. Python 操作 String 类型

```python
# 设置字符串
r.set('name', '小明')

# 获取字符串
name = r.get('name')
print(name)  # 输出：小明

# 追加字符串
r.append('name', '是个好同学')
print(r.get('name'))  # 输出：小明是个好同学

# 设置过期时间
r.setex('code', 60, '123456')  # 验证码 60 秒后过期
```

**<font color='green'>Python 操作 Redis 就像操作字典一样简单！</font>**

### 3. Python 操作 Hash 类型

```python
# 设置哈希字段值
r.hset('user:1', 'name', '张三')
r.hset('user:1', 'age', 25)

# 或者一次设置多个字段
r.hset('user:2', mapping={'name': '李四', 'age': 30, 'city': '上海'})

# 获取哈希字段值
name = r.hget('user:1', 'name')
print(name)  # 输出：张三

# 获取所有哈希字段和值
user_info = r.hgetall('user:1')
print(user_info)  # 输出：{'name': '张三', 'age': '25'}
```

### 4. Python 操作 List 类型

```python
# 向列表左侧插入元素
r.lpush('messages', '最新消息3', '最新消息2', '最新消息1')

# 向列表右侧插入元素
r.rpush('messages', '较早消息1', '较早消息2')

# 获取列表指定范围元素
messages = r.lrange('messages', 0, -1)
print(messages)  # 输出：['最新消息1', '最新消息2', '最新消息3', '较早消息1', '较早消息2']

# 从列表左侧弹出元素
latest = r.lpop('messages')
print(latest)  # 输出：最新消息1
```

### 5. Python 操作 Set 类型

```python
# 向集合添加元素
r.sadd('friends', '小明', '小红', '小刚')

# 判断元素是否在集合中
is_member = r.sismember('friends', '小明')
print(is_member)  # 输出：True

# 获取集合所有元素
friends = r.smembers('friends')
print(friends)  # 输出：{'小明', '小红', '小刚'}

# 集合间的操作
r.sadd('group1', 'A', 'B', 'C')
r.sadd('group2', 'B', 'C', 'D')
print(r.sinter('group1', 'group2'))  # 输出：{'B', 'C'}
```

### 6. Python 操作 ZSet 类型

```python
# 向有序集合添加元素
r.zadd('scores', {'小明': 89, '小红': 92, '小刚': 76})

# 获取有序集合指定范围元素
students = r.zrange('scores', 0, -1, withscores=True)
print(students)  # 输出：[('小刚', 76.0), ('小明', 89.0), ('小红', 92.0)]

# 获取元素的分数
score = r.zscore('scores', '小红')
print(score)  # 输出：92.0
```

### 7. Redis 事务操作

**<font color='red'>Redis 事务可以一次执行多个命令，保证原子性：</font>**

```python
# 开启事务
pipe = r.pipeline(transaction=True)

# 添加命令到事务
pipe.set('name', '小明')
pipe.incr('age')
pipe.sadd('friends', '小红')

# 执行事务
result = pipe.execute()
print(result)  # 输出执行结果列表

# 放弃事务
pipe.reset()
```

### 8. Redis 管道操作

**<font color='blue'>管道可以批量执行命令，减少网络往返次数：</font>**

```python
# 创建管道对象
pipe = r.pipeline()

# 添加命令到管道
for i in range(100):
    pipe.set(f'key:{i}', f'value:{i}')

# 执行管道中的所有命令
result = pipe.execute()
```

### 9. Redis 发布与订阅

**<font color='purple'>发布订阅模式就像微信公众号：</font>**

```python
# 发布者代码
r.publish('channel:news', '今天有重大新闻！')

# 订阅者代码
pubsub = r.pubsub()
pubsub.subscribe('channel:news')

# 监听消息
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"收到消息：{message['data']}")
```

## 应用场景

**<font color='green'>Redis 在实际项目中有这些超赞的应用：</font>**

1. **缓存系统**：存储热点数据，减轻数据库压力
2. **计数器**：高并发计数，如文章阅读量、点赞数
3. **限流器**：控制 API 访问频率，防止恶意请求
4. **排行榜**：使用 ZSet 实现实时排行榜
5. **会话存储**：存储用户会话信息，实现分布式 Session
6. **消息队列**：使用 List 或发布订阅实现简单的消息队列
7. **地理位置**：使用 GEO 命令实现附近的人、店铺等功能

## 总结

**<font color='red'>Redis 就像数据世界的"闪电侠"：</font>**

1. **速度极快**：基于内存操作，读写性能惊人
2. **类型丰富**：五种基本数据类型满足各种需求
3. **功能强大**：事务、管道、发布订阅等高级特性
4. **简单易用**：命令简洁，Python 接口友好

掌握了 Redis，你就拥有了一把解决高并发、缓存、实时数据处理的"瑞士军刀"！

**<font color='blue'>小作业：</font>** 尝试用 Redis 实现一个简单的投票系统，记录用户对不同选项的投票，并实时显示投票结果。

下一章，我们将探索 MongoDB 这个文档型数据库的奥秘，敬请期待！