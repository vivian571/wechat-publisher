# 第三章：多进程 - Python并发编程实战指南

## 学习目标

嘿，小伙伴们！今天咱们要聊的是Python中的**<font color="red">多进程编程</font>**。学完这一章，你将：

- 理解**<font color="blue">进程的基本概念</font>**和它与程序的区别
- 掌握Python中**<font color="green">创建和管理多进程</font>**的方法
- 学会使用**<font color="purple">进程间通信</font>**的各种技术
- 能够在实际项目中**<font color="orange">合理应用多进程</font>**提升程序性能

## 知识点详解

### 什么是进程？

简单来说，**<font color="red">进程就是一个正在运行中的程序</font>**。当你双击打开微信，操作系统就会为微信这个程序创建一个进程。每个进程都有自己独立的内存空间，互不干扰。

程序和进程的区别可以这样理解：程序就像是放在书架上的食谱，而进程则是按照这个食谱实际做菜的过程。同一本食谱可以同时被多个厨师使用（多个进程），每个厨师都有自己的灶台和食材（独立的内存空间）。

### 进程的状态

进程在运行过程中会经历不同的状态：

- **<font color="blue">就绪状态</font>**：进程已经准备好了，就等CPU来执行它了，就像你排队等待坐过山车一样。
- **<font color="green">运行状态</font>**：CPU正在执行这个进程的指令，相当于你已经坐上过山车开始游玩了。
- **<font color="purple">阻塞状态</font>**：进程因为等待某些资源（比如用户输入、文件读写）而暂停执行，就像过山车中途停下来等待前面的车辆通过。

进程状态之间会相互转换。比如，当一个运行中的进程需要读取硬盘上的大文件时，它会从运行状态变为阻塞状态；当文件读取完成后，它又会变回就绪状态，等待CPU再次执行它。

### 进程的创建 - multiprocessing

在Python中，我们主要使用**<font color="red">multiprocessing模块</font>**来创建和管理进程。下面是一些基本用法：

#### 两个while循环一起执行

```python
import multiprocessing
import time

def task1():
    while True:
        print("我是任务1，正在执行...")
        time.sleep(1)

def task2():
    while True:
        print("我是任务2，也在执行...")
        time.sleep(1)

if __name__ == "__main__":
    # 创建两个进程
    p1 = multiprocessing.Process(target=task1)
    p2 = multiprocessing.Process(target=task2)
    
    # 启动进程
    p1.start()
    p2.start()
```

运行上面的代码，你会发现两个任务真的是**同时执行**的！这就是多进程的魅力 - 它能让你的程序同时做多件事。

#### 获取进程的pid

每个进程都有一个唯一的标识符，叫做PID（进程ID）。我们可以通过`os.getpid()`获取当前进程的ID，通过`os.getppid()`获取父进程的ID：

```python
import multiprocessing
import os

def worker():
    print(f"我是子进程，我的PID是：{os.getpid()}")
    print(f"我爸爸（父进程）的PID是：{os.getppid()}")

if __name__ == "__main__":
    print(f"我是主进程，我的PID是：{os.getpid()}")
    
    p = multiprocessing.Process(target=worker)
    p.start()
    p.join()  # 等待子进程结束
```

#### 给子进程指定的函数传递参数

创建进程时，我们可以通过`args`或`kwargs`参数向子进程的函数传递参数：

```python
import multiprocessing

def worker(name, age, **kwargs):
    print(f"我是{name}，今年{age}岁")
    for k, v in kwargs.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    # 使用args传递位置参数
    p1 = multiprocessing.Process(target=worker, args=("张三", 25))
    
    # 使用kwargs传递关键字参数
    p2 = multiprocessing.Process(target=worker, 
                               args=("李四", 30), 
                               kwargs={"城市": "北京", "爱好": "编程"})
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

#### 进程间不共享全局变量

这一点非常重要！**<font color="red">多进程之间不共享全局变量</font>**，每个进程都有自己独立的内存空间。看下面的例子：

```python
import multiprocessing
import time

# 全局变量
_number = 0

def add():
    global _number
    for _ in range(1000000):
        _number += 1
    print(f"子进程中，_number = {_number}")

if __name__ == "__main__":
    p = multiprocessing.Process(target=add)
    p.start()
    p.join()
    
    # 主进程中的全局变量没有改变
    print(f"主进程中，_number = {_number}")
```

运行结果会是：
```
子进程中，_number = 1000000
主进程中，_number = 0
```

这说明子进程对全局变量的修改不会影响主进程中的值，因为它们是完全独立的内存空间。这与多线程共享全局变量的行为完全不同！

### 进程、线程对比

说到这里，咱们来对比一下**<font color="blue">进程和线程</font>**的区别：

| 特性 | 进程 | 线程 |
|------|------|------|
| 定义 | 资源分配的基本单位 | 程序执行的最小单位 |
| 内存空间 | 独立内存空间 | 共享所属进程的内存 |
| 通信方式 | 需要特殊的IPC机制 | 直接共享变量即可 |
| 切换开销 | 大 | 小 |
| 并行能力 | 可以在多核上并行 | 受GIL限制（Python） |
| 健壮性 | 一个进程崩溃不影响其他进程 | 一个线程崩溃可能导致整个进程崩溃 |

简单来说：
- 进程就像是不同的厨师在不同的厨房做菜
- 线程就像是一个厨师的两只手同时做不同的事

### 进程间的通信 - Queue

既然进程间不能直接共享变量，那么它们要如何通信呢？Python提供了多种进程间通信的方式，最常用的是**<font color="green">Queue（队列）</font>**：

```python
import multiprocessing

def producer(queue):
    for i in range(5):
        item = f"产品{i}"
        queue.put(item)  # 将数据放入队列
        print(f"生产者生产了: {item}")

def consumer(queue):
    for i in range(5):
        item = queue.get()  # 从队列获取数据
        print(f"消费者消费了: {item}")

if __name__ == "__main__":
    # 创建一个队列
    q = multiprocessing.Queue()
    
    # 创建生产者和消费者进程
    p1 = multiprocessing.Process(target=producer, args=(q,))
    p2 = multiprocessing.Process(target=consumer, args=(q,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

这个例子展示了经典的**<font color="purple">生产者-消费者模型</font>**，两个进程通过队列进行数据交换。

### 进程池的创建 - Pool

如果你需要创建大量的进程，一个一个地创建和管理会很麻烦。这时候就可以使用**<font color="orange">进程池（Pool）</font>**：

```python
import multiprocessing
import os
import time

def worker(x):
    print(f"进程 {os.getpid()} 处理数据: {x}")
    time.sleep(1)  # 模拟耗时操作
    return x * x

if __name__ == "__main__":
    # 创建一个包含4个进程的进程池
    pool = multiprocessing.Pool(processes=4)
    
    # 将数据分配给进程池处理
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    results = pool.map(worker, data)
    
    # 关闭进程池
    pool.close()
    pool.join()
    
    print(f"处理结果: {results}")
```

进程池会自动管理进程的创建和销毁，并且能够重用进程，提高效率。

### 进程池代码的执行方式

进程池提供了多种任务提交方式：

#### 同步执行

```python
# 使用apply方法同步执行任务
result = pool.apply(worker, args=(5,))
```

`apply`方法会阻塞主进程，直到子进程执行完毕并返回结果。

#### 异步执行

```python
# 使用apply_async方法异步执行任务
result = pool.apply_async(worker, args=(5,))

# 获取结果（会阻塞直到结果可用）
value = result.get()
```

`apply_async`方法不会阻塞主进程，它立即返回一个结果对象，你可以在需要结果时调用`get()`方法获取。

### 进程间通信的其他方式

除了Queue，Python还提供了其他进程间通信的方式：

#### 管道（Pipe）

```python
import multiprocessing

def sender(conn):
    conn.send("你好，我是发送者")
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f"收到消息: {msg}")
    conn.close()

if __name__ == "__main__":
    # 创建一个管道
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # 创建发送和接收进程
    p1 = multiprocessing.Process(target=sender, args=(parent_conn,))
    p2 = multiprocessing.Process(target=receiver, args=(child_conn,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

#### 共享内存（Value和Array）

```python
import multiprocessing

def add_value(value):
    value.value += 100
    print(f"子进程中，value = {value.value}")

if __name__ == "__main__":
    # 创建一个共享整数
    shared_value = multiprocessing.Value('i', 0)
    print(f"初始值: {shared_value.value}")
    
    p = multiprocessing.Process(target=add_value, args=(shared_value,))
    p.start()
    p.join()
    
    print(f"主进程中，value = {shared_value.value}")
```

#### 信号量（Semaphore）

```python
import multiprocessing
import time

def worker(semaphore, i):
    print(f"进程 {i} 等待信号量...")
    semaphore.acquire()  # 获取信号量
    print(f"进程 {i} 获得信号量")
    time.sleep(1)  # 模拟工作
    print(f"进程 {i} 释放信号量")
    semaphore.release()  # 释放信号量

if __name__ == "__main__":
    # 创建一个信号量，最多允许2个进程同时访问
    semaphore = multiprocessing.Semaphore(2)
    
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(semaphore, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
```

## 应用场景

多进程编程在哪些场景下特别有用呢？

### CPU密集型任务

如果你的程序需要进行大量计算，比如**<font color="red">图像处理、视频编码、科学计算</font>**等，多进程可以充分利用多核CPU的优势，显著提升性能。

```python
# 使用多进程处理图像
import multiprocessing
from PIL import Image, ImageFilter
import os

def process_image(image_path, output_path):
    img = Image.open(image_path)
    img = img.filter(ImageFilter.GaussianBlur(5))
    img.save(output_path)
    print(f"处理完成: {image_path}")

if __name__ == "__main__":
    image_dir = "images"
    output_dir = "processed_images"
    os.makedirs(output_dir, exist_ok=True)
    
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))]
    
    pool = multiprocessing.Pool(processes=os.cpu_count())
    
    for image_file in image_files:
        input_path = os.path.join(image_dir, image_file)
        output_path = os.path.join(output_dir, image_file)
        pool.apply_async(process_image, args=(input_path, output_path))
    
    pool.close()
    pool.join()
```

### 分布式计算

多进程也是**<font color="blue">分布式计算</font>**的基础。比如，你可以用多进程实现一个简单的分布式爬虫：

```python
import multiprocessing
import requests
from bs4 import BeautifulSoup

def crawl(url, result_queue):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.text if soup.title else "无标题"
        result_queue.put((url, title))
        print(f"爬取成功: {url}")
    except Exception as e:
        print(f"爬取失败: {url}, 错误: {e}")

if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.reddit.com",
        "https://www.wikipedia.org"
    ]
    
    result_queue = multiprocessing.Queue()
    processes = []
    
    for url in urls:
        p = multiprocessing.Process(target=crawl, args=(url, result_queue))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    # 收集结果
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    for url, title in results:
        print(f"URL: {url}, 标题: {title}")
```

## 总结

好啦，小伙伴们！今天我们学习了Python中的多进程编程，包括：

- 进程的基本概念和状态
- 使用multiprocessing模块创建和管理进程
- 进程间通信的多种方式（Queue、Pipe、共享内存、信号量）
- 进程池的使用和执行方式
- 多进程的实际应用场景

记住，**<font color="red">多进程适合CPU密集型任务</font>**，可以真正利用多核CPU的优势；而**<font color="blue">多线程适合IO密集型任务</font>**，可以在等待IO时执行其他任务。

在实际开发中，你需要根据任务特性选择合适的并发模型。有时候，甚至可以**<font color="green">混合使用多进程和多线程</font>**，发挥各自的优势。

下一章，我们将学习Python中的协程和异步编程，敬请期待！

## 思考题

1. 如果你需要开发一个网络爬虫，你会选择多进程还是多线程？为什么？
2. 多进程和多线程各有什么优缺点？在什么场景下应该选择多进程？
3. 尝试使用多进程实现一个简单的并行计算程序，比如计算大量数字的平方和。

欢迎在评论区分享你的想法和代码实现！