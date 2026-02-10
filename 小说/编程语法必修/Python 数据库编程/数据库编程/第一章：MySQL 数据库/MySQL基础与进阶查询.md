# MySQL基础与进阶查询：从小白到大神的进阶之路

嘿，小伙伴们！今天咱们来聊聊数据库界的"扛把子"——**MySQL**！

你是不是经常听到有人说："我们的数据存在MySQL里"、"这个网站后台用的是MySQL"？没错，这家伙可是互联网世界的"**数据管家**"，几乎所有网站和App背后都有它的身影！

## 学习目标

通过这篇文章，你将：

1. 掌握 **<font color="#E74C3C">MySQL的基础知识</font>**，包括数据类型、约束和基本操作
2. 学会 **<font color="#3498DB">进阶查询技巧</font>**，让你的数据库操作更加高效
3. 通过 **<font color="#2ECC71">实战案例</font>** 理解MySQL在实际项目中的应用

废话不多说，咱们直接上干货！

## 一、MySQL基础知识

### 1. 数据类型：给数据穿上"合身的衣服"

MySQL里的数据类型就像是给不同数据穿的"衣服"，选对了类型，数据存取又快又省空间！

**<font color="#E74C3C">数值类型</font>**：整数用`INT`，小数用`DECIMAL`，超小整数用`TINYINT`。

**<font color="#3498DB">字符串类型</font>**：定长字符用`CHAR`，变长字符用`VARCHAR`，大文本用`TEXT`。

**<font color="#2ECC71">时间日期类型</font>**：日期用`DATE`，时间用`TIME`，日期+时间用`DATETIME`。

**<font color="#F39C12">二进制类型</font>**：存图片、文件用`BLOB`。

选数据类型就像买衣服，太大浪费空间，太小撑破数据，要"量体裁衣"！

### 2. 约束：给数据立规矩

约束就是数据库的"规矩"，让你的数据更规范、更可靠！

**<font color="#E74C3C">主键约束(PRIMARY KEY)</font>**：相当于数据的"身份证"，唯一标识，不能重复，不能为空。

**<font color="#3498DB">非空约束(NOT NULL)</font>**：这个字段不能空着，必须填值！

**<font color="#2ECC71">唯一约束(UNIQUE)</font>**：值不能重复，但可以为NULL。

**<font color="#F39C12">外键约束(FOREIGN KEY)</font>**：建立表之间的关系，保证数据的一致性。

**<font color="#9B59B6">默认值(DEFAULT)</font>**：如果没填，就用这个默认值。

**<font color="#34495E">检查约束(CHECK)</font>**：设定值的范围，比如年龄必须>0。

约束就像是"保安"，把不合格的数据拦在门外！

### 3. 数据库操作：MySQL的"房产管理"

数据库就像是一栋大楼，需要好好管理！

**<font color="#E74C3C">创建数据库</font>**：
```sql
CREATE DATABASE 数据库名;
```

**<font color="#3498DB">查看所有数据库</font>**：
```sql
SHOW DATABASES;
```

**<font color="#2ECC71">使用数据库</font>**：
```sql
USE 数据库名;
```

**<font color="#F39C12">删除数据库</font>**：
```sql
DROP DATABASE 数据库名;
```

记住，删库跑路可不是闹着玩的，删除前一定要三思！

### 4. 数据表操作：给数据安个"家"

表就是数据的"家"，需要精心设计！

**<font color="#E74C3C">创建表</font>**：
```sql
CREATE TABLE 表名(
   字段名1 数据类型 [约束],
   字段名2 数据类型 [约束],
   ...
);
```

**<font color="#3498DB">查看所有表</font>**：
```sql
SHOW TABLES;
```

**<font color="#2ECC71">查看表结构</font>**：
```sql
DESC 表名;
```

**<font color="#F39C12">修改表</font>**：
```sql
ALTER TABLE 表名 ADD 字段名 数据类型 [约束];
```

**<font color="#9B59B6">删除表</font>**：
```sql
DROP TABLE 表名;
```

表结构设计得好，后面的操作才能顺风顺水！

### 5. 增删改查：数据的"日常生活"

这是数据库最常用的操作，也是最基础的技能！

**<font color="#E74C3C">添加数据(INSERT)</font>**：
```sql
INSERT INTO 表名(字段1, 字段2) VALUES(值1, 值2);
```

**<font color="#3498DB">查询数据(SELECT)</font>**：
```sql
SELECT 字段1, 字段2 FROM 表名 WHERE 条件;
```

**<font color="#2ECC71">更新数据(UPDATE)</font>**：
```sql
UPDATE 表名 SET 字段1=值1, 字段2=值2 WHERE 条件;
```

**<font color="#F39C12">删除数据(DELETE)</font>**：
```sql
DELETE FROM 表名 WHERE 条件;
```

增删改查就像数据的"吃喝拉撒睡"，是数据库操作的基本功！

## 二、MySQL进阶查询

基础打好了，咱们来点"高级操作"，让你的SQL技能更上一层楼！

### 1. 创建数据库和数据表

学习查询前，先准备点"素材"！

**<font color="#E74C3C">数据准备</font>**：

```sql
-- 创建学生管理数据库
CREATE DATABASE student_db;
USE student_db;

-- 创建学生表
CREATE TABLE students(
   id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(50) NOT NULL,
   age INT CHECK(age > 0),
   gender CHAR(1),
   class_id INT,
   score DECIMAL(5,2)
);

-- 插入测试数据
INSERT INTO students VALUES
(1, '张三', 18, '男', 101, 89.5),
(2, '李四', 19, '男', 102, 76.8),
(3, '王五', 20, '男', 101, 92.0),
(4, '赵六', 18, '女', 102, 85.5),
(5, '钱七', 19, '女', 101, 91.0);
```

**<font color="#3498DB">消除重复行</font>**：

```sql
SELECT DISTINCT class_id FROM students;
```

`DISTINCT`关键字就像"去重神器"，重复的值只显示一次！

### 2. 条件查询：找到你想要的数据

条件查询就像是"筛选器"，帮你从海量数据中找到需要的那部分！

**<font color="#E74C3C">比较运算符</font>**：

```sql
-- 查找成绩大于90分的学生
SELECT * FROM students WHERE score > 90;

-- 查找不是101班的学生
SELECT * FROM students WHERE class_id <> 101;
```

**<font color="#3498DB">逻辑运算符</font>**：

```sql
-- 查找101班且成绩大于90的学生
SELECT * FROM students WHERE class_id = 101 AND score > 90;

-- 查找年龄是18或19的学生
SELECT * FROM students WHERE age = 18 OR age = 19;
```

**<font color="#2ECC71">模糊查询</font>**：

```sql
-- 查找名字中包含'张'的学生
SELECT * FROM students WHERE name LIKE '%张%';

-- 查找名字以'李'开头的学生
SELECT * FROM students WHERE name LIKE '李%';
```

**<font color="#F39C12">范围查询</font>**：

```sql
-- 查找成绩在80到90之间的学生
SELECT * FROM students WHERE score BETWEEN 80 AND 90;

-- 查找101班或102班的学生
SELECT * FROM students WHERE class_id IN (101, 102);
```

**<font color="#9B59B6">空值判断</font>**：

```sql
-- 查找没有填写性别的学生
SELECT * FROM students WHERE gender IS NULL;

-- 查找有填写性别的学生
SELECT * FROM students WHERE gender IS NOT NULL;
```

**<font color="#34495E">优先级</font>**：

记住，AND的优先级高于OR，如果有疑问，就加括号！

```sql
-- 查找101班的男生或者所有的女生
SELECT * FROM students WHERE (class_id = 101 AND gender = '男') OR gender = '女';
```

### 3. 排序：数据排排坐

排序就像是给数据"排队"，按照特定的规则排列！

**<font color="#E74C3C">升序(ASC)</font>**：

```sql
-- 按年龄从小到大排序
SELECT * FROM students ORDER BY age ASC;
```

**<font color="#3498DB">降序(DESC)</font>**：

```sql
-- 按成绩从高到低排序
SELECT * FROM students ORDER BY score DESC;
```

**<font color="#2ECC71">组合排序</font>**：

```sql
-- 先按班级排序，班级相同再按成绩从高到低排序
SELECT * FROM students ORDER BY class_id ASC, score DESC;
```

排序就像是数据的"队列管理员"，让数据按照你想要的顺序排好队！

### 4. 聚合函数：数据的"总管"

聚合函数就像是数据的"总管"，可以对一组数据进行统计计算！

**<font color="#E74C3C">总数(COUNT)</font>**：

```sql
-- 统计学生总人数
SELECT COUNT(*) AS 学生总数 FROM students;

-- 统计101班的学生人数
SELECT COUNT(*) AS 班级人数 FROM students WHERE class_id = 101;
```

**<font color="#3498DB">最大值(MAX)</font>**：

```sql
-- 查找最高成绩
SELECT MAX(score) AS 最高分 FROM students;
```

**<font color="#2ECC71">最小值(MIN)</font>**：

```sql
-- 查找最低成绩
SELECT MIN(score) AS 最低分 FROM students;
```

**<font color="#F39C12">求和(SUM)</font>**：

```sql
-- 计算所有学生的总成绩
SELECT SUM(score) AS 总成绩 FROM students;
```

**<font color="#9B59B6">平均值(AVG)</font>**：

```sql
-- 计算平均成绩
SELECT AVG(score) AS 平均分 FROM students;
```

聚合函数就像是数据的"计算器"，帮你快速得到统计结果！

### 5. 分组：数据的"小团体"

分组就像是给数据分"小团体"，然后对每个"团体"进行统计！

**<font color="#E74C3C">GROUP BY</font>**：

```sql
-- 按班级分组
SELECT class_id FROM students GROUP BY class_id;
```

**<font color="#3498DB">GROUP BY + GROUP_CONCAT()</font>**：

```sql
-- 查看每个班级都有哪些学生
SELECT class_id, GROUP_CONCAT(name) AS 学生列表 FROM students GROUP BY class_id;
```

**<font color="#2ECC71">GROUP BY + 聚合函数</font>**：

```sql
-- 统计每个班级的人数
SELECT class_id, COUNT(*) AS 班级人数 FROM students GROUP BY class_id;

-- 统计每个班级的平均成绩
SELECT class_id, AVG(score) AS 平均分 FROM students GROUP BY class_id;
```

**<font color="#F39C12">GROUP BY + HAVING</font>**：

```sql
-- 查找平均成绩大于85分的班级
SELECT class_id, AVG(score) AS 平均分 
FROM students 
GROUP BY class_id 
HAVING AVG(score) > 85;
```

**<font color="#9B59B6">GROUP BY + WITH ROLLUP</font>**：

```sql
-- 统计每个班级的人数，并在最后显示总人数
SELECT class_id, COUNT(*) AS 人数 
FROM students 
GROUP BY class_id WITH ROLLUP;
```

分组查询就像是数据的"团队报表"，让你快速了解各个"小团体"的情况！

### 6. 分页：数据的"翻页器"

分页就像是给数据做了个"翻页器"，每次只看一部分数据！

**<font color="#E74C3C">获取部分行数据</font>**：

```sql
-- 获取前3条数据（第1页，每页3条）
SELECT * FROM students LIMIT 3;

-- 获取第4-6条数据（第2页，每页3条）
SELECT * FROM students LIMIT 3, 3;

-- 或者使用OFFSET关键字
SELECT * FROM students LIMIT 3 OFFSET 3;
```

分页查询在网站开发中超级常用，比如商品列表、文章列表等，都需要分页显示！

### 7. 连接查询：表的"联姻"

连接查询就像是表的"联姻"，把多个表的数据关联起来查询！

假设我们再创建一个班级表：

```sql
CREATE TABLE classes(
   id INT PRIMARY KEY,
   class_name VARCHAR(50) NOT NULL,
   teacher VARCHAR(50)
);

INSERT INTO classes VALUES
(101, '高一(1)班', '张老师'),
(102, '高一(2)班', '李老师');
```

**<font color="#E74C3C">内连接查询(INNER JOIN)</font>**：

```sql
-- 查询学生及其所在班级的信息
SELECT s.name, s.score, c.class_name, c.teacher
FROM students s
INNER JOIN classes c ON s.class_id = c.id;
```

内连接只显示两个表中能关联上的数据！

**<font color="#3498DB">左连接查询(LEFT JOIN)</font>**：

```sql
-- 查询所有学生及其班级信息，包括没有班级的学生
SELECT s.name, s.score, c.class_name, c.teacher
FROM students s
LEFT JOIN classes c ON s.class_id = c.id;
```

左连接会显示左表的所有数据，即使在右表中没有匹配的记录！

**<font color="#2ECC71">右连接查询(RIGHT JOIN)</font>**：

```sql
-- 查询所有班级及其学生信息，包括没有学生的班级
SELECT s.name, s.score, c.class_name, c.teacher
FROM students s
RIGHT JOIN classes c ON s.class_id = c.id;
```

右连接会显示右表的所有数据，即使在左表中没有匹配的记录！

**<font color="#F39C12">自关联查询</font>**：

假设我们有一个员工表，包含员工ID和其上级ID：

```sql
CREATE TABLE employees(
   id INT PRIMARY KEY,
   name VARCHAR(50),
   manager_id INT
);

-- 查询员工及其上级的姓名
SELECT e1.name AS 员工, e2.name AS 上级
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.id;
```

自关联查询就是表和自己进行连接，通常用于处理树形结构的数据！

**<font color="#9B59B6">子查询</font>**：

```sql
-- 查询成绩高于平均分的学生
SELECT * FROM students
WHERE score > (SELECT AVG(score) FROM students);

-- 查询班级人数最多的班级
SELECT class_id, COUNT(*) AS 人数
FROM students
GROUP BY class_id
HAVING 人数 = (
   SELECT COUNT(*) AS cnt
   FROM students
   GROUP BY class_id
   ORDER BY cnt DESC
   LIMIT 1
);
```

子查询就像是"查询套查询"，可以在一个查询中嵌套另一个查询！

## 应用场景

MySQL在实际项目中的应用非常广泛，几乎所有需要存储和管理数据的系统都离不开它！

**<font color="#E74C3C">电商网站</font>**：存储商品信息、用户信息、订单信息等。

**<font color="#3498DB">博客系统</font>**：存储文章、评论、用户等数据。

**<font color="#2ECC71">企业管理系统</font>**：存储员工信息、部门信息、工资信息等。

**<font color="#F39C12">社交网络</font>**：存储用户信息、好友关系、消息等数据。

**<font color="#9B59B6">游戏系统</font>**：存储玩家信息、游戏道具、交易记录等。

## 总结

通过这篇文章，我们学习了MySQL的基础知识和进阶查询技巧，从数据类型、约束、基本操作到条件查询、排序、分组、连接查询等高级技能。

MySQL就像是数据的"管家"，帮你管理和组织各种数据，是开发者必备的技能之一！

掌握了这些技能，你就能轻松应对各种数据库操作需求，成为数据库操作的高手！

下一篇，我们将深入探讨MySQL的索引优化和性能调优，敬请期待！

你有什么关于MySQL的问题或经验，欢迎在评论区留言分享哦！