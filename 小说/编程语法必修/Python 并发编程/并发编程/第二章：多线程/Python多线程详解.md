# 第二章：多线程 - Python并发编程实战指南

## 学习目标

- **<font color="red">理解线程和进程的本质区别</font>**
- **<font color="blue">掌握Python多线程的创建与使用</font>**
- **<font color="green">学会处理多线程共享变量问题</font>**
- **<font color="purple">熟练运用互斥锁解决资源竞争</font>**
- **<font color="orange">能够识别和预防死锁情况</font>**
- **<font color="brown">灵活应用线程池提高程序性能</font>**

## 知识点详解

### 线程和进程：傻傻分不清楚？

说实话，刚开始学编程的时候，我也被线程和进程这两个概念搞得一头雾水。它们听起来那么像，但又完全不同！

**<font color="red">线程是啥？</font>**简单说，线程就是程序执行的最小单元，是进程中的一个"小兄弟"。想象你在用手机时，微信可以一边接收消息，一边播放语音，这就是多线程在工作啦！

**<font color="blue">进程又是啥？</font>**进程就是一个正在运行的程序实例，比如你打开的微信就是一个进程。它是系统分配资源的基本单位，就像公司里的一个部门，有自己的"办公室"（内存空间）。

**<font color="green">它们有啥区别？</font>**

- 资源占用：进程像是独立的小王国，有自己的地盘；线程则像王国里的居民，共享王国的资源
- 调度开销：创建进程就像建立新公司，成本高；创建线程则像招新员工，成本低
- 通信难度：两个进程交流就像两家公司打电话，比较麻烦；线程间交流则像同事间聊天，简单多了

### 使用线程：Python多线程初体验

在Python中玩多线程，首先得了解一个"拦路虎" - **<font color="red">全局解释器锁(GIL)</font>**。

这个GIL是啥玩意儿？简单说，它就是Python解释器的一把大锁，同一时刻只允许一个线程执行Python字节码。这就尴尬了，多线程不是应该并行执行吗？

别急，GIL确实会限制CPU密集型任务的性能，但对I/O密集型任务（如网络请求、文件操作）影响不大。因为I/O操作时，线程会释放GIL，让其他线程有机会执行。

**<font color="blue">多任务并发是啥概念？</font>**

- 并发：看起来同时执行（实际上是快速切换）
- 并行：真正的同时执行（需要多核CPU）

在Python中，多线程主要实现的是并发，而非并行（因为GIL的存在）。

**<font color="green">怎么创建线程？</font>**

```python
# 方法一：使用函数创建线程
import threading
import time

def 唱歌():
    print("我在唱歌...")
    time.sleep(1)
    print("唱完了！")

# 创建线程对象
t = threading.Thread(target=唱歌)
# 启动线程
t.start()

# 方法二：继承Thread类创建线程
class 跳舞线程(threading.Thread):
    def run(self):
        print("我在跳舞...")
        time.sleep(1)
        print("跳完了！")

# 创建并启动线程
t = 跳舞线程()
t.start()
```

**<font color="purple">主线程和子线程啥关系？</font>**

主线程就像是家长，子线程是孩子。默认情况下，即使所有孩子都睡了，家长还会继续忙碌。如果想让家长等所有孩子都睡了才休息，就需要用`join()`方法：

```python
import threading
import time

def 工作(name):
    print(f"{name}开始工作")
    time.sleep(2)
    print(f"{name}工作完成")

# 创建5个线程
threads = []
for i in range(5):
    t = threading.Thread(target=工作, args=(f"员工{i}",))
    threads.append(t)
    t.start()

# 主线程等待所有子线程完成
for t in threads:
    t.join()

print("所有人都下班了！")
```

**<font color="orange">怎么知道当前有几个线程在跑？</font>**

```python
import threading
print(f"当前活动线程数：{threading.active_count()}")
```

**<font color="brown">线程执行顺序能控制吗？</font>**

线程的执行顺序是不确定的，由操作系统调度决定。如果需要控制执行顺序，就需要用到同步机制，比如锁、信号量等。

### 多线程共享全局变量：一起玩一个球

多线程最大的特点就是共享进程的资源，包括全局变量。这就像几个人一起玩一个球，方便是方便，但也容易出问题。

**<font color="red">整型变量共享的坑：</font>**

```python
import threading
import time

# 全局变量
票数 = 100

def 卖票():
    global 票数
    for i in range(10):
        if 票数 > 0:
            time.sleep(0.01)  # 模拟网络延迟
            print(f"卖出一张票，剩余{票数-1}张")
            票数 -= 1

# 创建5个售票窗口（线程）
threads = []
for i in range(5):
    t = threading.Thread(target=卖票)
    threads.append(t)
    t.start()

# 等待所有线程结束
for t in threads:
    t.join()

print(f"最终剩余票数：{票数}")
```

运行这段代码，你可能会发现最终票数不是50，甚至可能出现"卖出一张票，剩余xx张"中的数字不对。这就是多线程共享变量的问题！

**<font color="blue">列表、字典共享也有坑：</font>**

```python
import threading

# 共享的列表
购物车 = []

def 添加商品(商品):
    购物车.append(商品)
    print(f"添加了{商品}，购物车现在有：{购物车}")

# 创建多个线程添加商品
threads = []
for i in range(5):
    t = threading.Thread(target=添加商品, args=(f"商品{i}",))
    threads.append(t)
    t.start()
```

列表操作看起来没问题，但如果多个线程同时修改同一个列表元素，还是会出现数据不一致的情况。

### 共享全局变量带来的问题：一场没有硝烟的战争

**<font color="red">资源竞争是啥？</font>**

想象一下，两个人同时去拿桌上最后一块蛋糕，结果打翻了盘子 - 这就是资源竞争！在程序中，当多个线程同时修改同一资源（如全局变量）时，就会发生资源竞争。

来看个经典例子：

```python
import threading

# 账户余额
余额 = 1000

def 取钱(金额):
    global 余额
    if 余额 >= 金额:
        # 模拟网络延迟
        import time
        time.sleep(0.1)
        余额 -= 金额
        print(f"取款{金额}元成功，剩余{余额}元")
    else:
        print("余额不足！")

# 创建两个线程同时取钱
t1 = threading.Thread(target=取钱, args=(800,))
t2 = threading.Thread(target=取钱, args=(800,))

t1.start()
t2.start()

t1.join()
t2.join()

print(f"最终余额：{余额}")
```

运行这段代码，你会发现两个线程都成功取了800元，最终余额变成-600元！这在现实生活中绝对是个大问题！

**<font color="blue">数据不一致是啥情况？</font>**

数据不一致就是指程序中的数据与现实不符。比如银行账户余额显示有1000元，但实际上已经被取空了。这种情况在多线程环境中很常见，因为线程之间的执行顺序是不确定的。

### 同步的概念：让线程排好队

**<font color="red">同步是啥意思？</font>**

同步就像是交通信号灯，让各个线程按照一定的规则执行，避免"车祸"（数据混乱）。通过同步机制，我们可以协调多个线程的执行顺序，确保共享资源的安全访问。

**<font color="blue">常见的同步方式有哪些？</font>**

- 互斥锁：一次只允许一个线程访问共享资源
- 信号量：控制同时访问共享资源的线程数量
- 条件变量：线程等待特定条件满足后再执行
- 事件：通知多个线程某个事件已经发生

### 互斥锁：给资源上把锁

**<font color="red">互斥锁怎么用？</font>**

```python
import threading

# 创建一把锁
锁 = threading.Lock()

# 账户余额
余额 = 1000

def 取钱(金额):
    global 余额
    # 获取锁
    锁.acquire()
    try:
        if 余额 >= 金额:
            # 模拟网络延迟
            import time
            time.sleep(0.1)
            余额 -= 金额
            print(f"取款{金额}元成功，剩余{余额}元")
        else:
            print("余额不足！")
    finally:
        # 释放锁
        锁.release()

# 创建两个线程同时取钱
t1 = threading.Thread(target=取钱, args=(800,))
t2 = threading.Thread(target=取钱, args=(800,))

t1.start()
t2.start()

t1.join()
t2.join()

print(f"最终余额：{余额}")
```

这次运行代码，你会发现第一个线程取款成功，第二个线程会提示余额不足，最终余额是200元 - 这才是正确的结果！

**<font color="blue">锁的工作原理是啥？</font>**

互斥锁就像厕所的门锁：
1. 一个线程获取锁（锁门）
2. 其他线程必须等待锁被释放（等待厕所空出来）
3. 线程用完资源后释放锁（开门出来）
4. 等待的线程竞争获取锁（争着进厕所）

**<font color="green">锁的粒度控制很重要！</font>**

- 粒度太大（锁的范围太广）：影响程序性能，因为线程要等待的时间变长
- 粒度太小（锁的范围太小）：可能无法完全保护共享资源

最佳实践是：只锁定真正需要保护的代码段，尽量减小锁的范围。

### 死锁：两个人互相礼让，结果都饿死了

**<font color="red">死锁是啥情况？</font>**

死锁就是两个或多个线程互相等待对方释放资源，导致所有线程都无法继续执行的情况。就像两个人互相礼让："你先走""不，你先走"，结果谁也不动。

**<font color="blue">死锁代码案例：</font>**

```python
import threading
import time

# 创建两把锁
筷子1 = threading.Lock()
筷子2 = threading.Lock()

def 哲学家1():
    print("哲学家1想吃饭")
    # 先拿起筷子1
    筷子1.acquire()
    print("哲学家1拿起了左边的筷子")
    time.sleep(0.5)  # 思考一下
    # 再拿起筷子2
    筷子2.acquire()
    print("哲学家1拿起了右边的筷子，开始吃饭")
    time.sleep(1)  # 吃饭
    # 放下筷子
    筷子2.release()
    筷子1.release()
    print("哲学家1吃完了")

def 哲学家2():
    print("哲学家2想吃饭")
    # 先拿起筷子2
    筷子2.acquire()
    print("哲学家2拿起了左边的筷子")
    time.sleep(0.5)  # 思考一下
    # 再拿起筷子1
    筷子1.acquire()
    print("哲学家2拿起了右边的筷子，开始吃饭")
    time.sleep(1)  # 吃饭
    # 放下筷子
    筷子1.release()
    筷子2.release()
    print("哲学家2吃完了")

# 创建两个线程
t1 = threading.Thread(target=哲学家1)
t2 = threading.Thread(target=哲学家2)

t1.start()
t2.start()
```

运行这段代码，你会发现两个哲学家都拿起了一只筷子，然后永远等待另一只筷子 - 这就是死锁！

**<font color="green">如何预防死锁？</font>**

1. 按顺序获取锁：确保所有线程以相同的顺序获取锁
2. 超时机制：设置获取锁的超时时间，超时后释放已获得的锁
3. 避免嵌套锁：尽量避免在持有一个锁的同时去获取另一个锁

### 线程池：员工复用，效率倍增

**<font color="red">线程池是啥？</font>**

线程池就像公司的固定员工团队，不需要每次都招聘新员工（创建新线程），而是反复使用现有员工（线程）来完成任务。这样可以：

- 减少线程创建和销毁的开销
- 控制并发线程数量，避免系统资源耗尽
- 提高响应速度，因为任务到达时可以立即执行

**<font color="blue">线程池怎么用？</font>**

```python
import concurrent.futures
import time

def 下载图片(图片编号):
    print(f"开始下载图片{图片编号}")
    time.sleep(1)  # 模拟下载耗时
    print(f"图片{图片编号}下载完成")
    return f"图片{图片编号}的数据"

# 创建线程池，最多5个线程
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as 线程池:
    # 提交10个下载任务
    任务列表 = []
    for i in range(10):
        任务 = 线程池.submit(下载图片, i)
        任务列表.append(任务)
    
    # 获取任务结果
    for 任务 in concurrent.futures.as_completed(任务列表):
        结果 = 任务.result()
        print(f"获取到结果：{结果}")
```

**<font color="green">线程池的应用场景：</font>**

- 网络爬虫：同时爬取多个网页
- 图片处理：并行处理多张图片
- 文件操作：同时读写多个文件
- 服务器应用：处理多个客户端请求

### 线程通信：让线程之间说说话

**<font color="red">队列实现线程通信：</font>**

```python
import threading
import queue
import time

# 创建一个队列
任务队列 = queue.Queue()

def 生产者():
    for i in range(10):
        任务 = f"任务{i}"
        任务队列.put(任务)
        print(f"生产者生产了：{任务}")
        time.sleep(0.5)

def 消费者():
    while True:
        任务 = 任务队列.get()
        print(f"消费者消费了：{任务}")
        # 标记任务完成
        任务队列.task_done()
        time.sleep(1)

# 创建生产者线程和消费者线程
生产者线程 = threading.Thread(target=生产者)
消费者线程 = threading.Thread(target=消费者, daemon=True)

消费者线程.start()
生产者线程.start()

生产者线程.join()
# 等待队列中所有任务被处理完
任务队列.join()
```

**<font color="blue">事件对象：</font>**

```python
import threading
import time

# 创建事件对象
开始信号 = threading.Event()

def 运动员(name):
    print(f"{name}已就位，等待发令枪")
    # 等待事件被设置
    开始信号.wait()
    print(f"{name}开始跑！")

# 创建多个运动员线程
threads = []
for i in range(5):
    t = threading.Thread(target=运动员, args=(f"运动员{i}",))
    threads.append(t)
    t.start()

# 裁判准备
time.sleep(3)
print("预备，跑！")
# 设置事件，通知所有线程
开始信号.set()

# 等待所有运动员跑完
for t in threads:
    t.join()
```

**<font color="green">条件变量：</font>**

```python
import threading
import time

# 创建条件变量
条件 = threading.Condition()
# 共享数据
数据 = []

def 生产者():
    with 条件:
        print("生产者生产数据...")
        数据.append("新数据")
        # 通知等待的消费者
        条件.notify()

def 消费者():
    with 条件:
        # 等待数据
        while not 数据:
            print("消费者等待数据...")
            条件.wait()
        # 消费数据
        数据.pop()
        print("消费者消费了数据")

# 创建线程
t1 = threading.Thread(target=消费者)
t2 = threading.Thread(target=生产者)

t1.start()
time.sleep(1)  # 确保消费者先等待
t2.start()

t1.join()
t2.join()
```

## 典型示例

### 多线程爬虫：并发下载网页

```python
import threading
import requests
import time

def 下载网页(url):
    print(f"开始下载：{url}")
    response = requests.get(url)
    print(f"下载完成：{url}，大小：{len(response.text)}字节")

# 要下载的网页列表
网页列表 = [
    "https://www.baidu.com",
    "https://www.sina.com.cn",
    "https://www.qq.com",
    "https://www.163.com",
    "https://www.sohu.com"
]

# 创建线程列表
threads = []
for url in 网页列表:
    t = threading.Thread(target=下载网页, args=(url,))
    threads.append(t)

# 记录开始时间
开始时间 = time.time()

# 启动所有线程
for t in threads:
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

# 计算总耗时
耗时 = time.time() - 开始时间
print(f"总耗时：{耗时:.2f}秒")
```

### 多线程文件处理：并行处理多个文件

```python
import threading
import os
import time

def 处理文件(文件名):
    print(f"开始处理文件：{文件名}")
    # 模拟文件处理耗时
    time.sleep(2)
    # 创建处理结果文件
    with open(f"{文件名}.处理结果", "w") as f:
        f.write(f"文件{文件名}处理完成")
    print(f"文件{文件名}处理完成")

# 要处理的文件列表
文件列表 = [f"文件{i}" for i in range(10)]

# 创建线程列表
threads = []
for 文件名 in 文件列表:
    t = threading.Thread(target=处理文件, args=(文件名,))
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

print("所有文件处理完成！")
```

## 应用场景

**<font color="red">1. 网络爬虫</font>**

多线程爬虫可以同时爬取多个网页，大大提高爬取效率。特别是对于I/O密集型的爬虫任务，使用多线程可以在等待网络响应的同时处理其他请求，充分利用CPU资源。

**<font color="blue">2. GUI应用程序</font>**

在图形界面应用中，通常需要一个主线程处理用户界面，同时用其他线程执行耗时操作（如文件读写、网络请求等），避免界面卡顿，提升用户体验。

**<font color="green">3. 服务器应用</font>**

服务器需要同时处理多个客户端请求，多线程可以让服务器并发处理这些请求，提高服务器的吞吐量和响应速度。

**<font color="purple">4. 文件处理</font>**

当需要处理大量文件时，可以使用多线程并行处理这些文件，充分利用多核CPU的优势，加快处理速度。

**<font color="orange">5. 定时任务</font>**

可以创建后台线程定期执行某些任务（如数据备份、日志清理等），而不影响主程序的运行。

## 总结

**<font color="red">多线程是把双刃剑！</font>**

- **优点**：提高程序响应速度，充分利用CPU资源，特别适合I/O密集型任务
- **缺点**：增加程序复杂度，可能引入资源竞争、死锁等问题，受GIL限制

**<font color="blue">使用多线程的最佳实践：</font>**

1. 合理使用锁保护共享资源，但要避免过度使用锁
2. 尽量减小锁的粒度，只锁定必要的代码段
3. 避免死锁，按固定顺序获取多个锁
4. 使用线程池控制线程数量，避免创建过多线程
5. 对于CPU密集型任务，考虑使用多进程而非多线程

**<font color="green">记住：</font>**多线程不是万能药，有时候单线程+异步IO或者多进程可能是更好的选择。选择合适的并发模型，取决于你的具体应用场景和性能需求。

学会了多线程编程，你就掌握了并发编程的基础，可以开发出更高效、响应更快的Python应用程序！下一章，我们将探索多进程编程，敬请期待！