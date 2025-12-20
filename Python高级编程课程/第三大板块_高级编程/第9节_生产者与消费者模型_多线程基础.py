# 第9节: 生产者与消费者模型、多线程基础
# 内容: 生产者与消费者模型、线程

import threading
import queue
import time
import random

# --- 1. 生产者与消费者模型 (使用 queue) ---
print("--- 1. 生产者与消费者模型示例 ---")

# 创建一个线程安全的队列
work_queue = queue.Queue(maxsize=5) # 设置队列最大容量为5

class Producer(threading.Thread):
    """生产者线程"""
    def run(self):
        print(f"生产者 {self.name} 启动...")
        for i in range(10):
            item = f"产品 {i}"
            try:
                # 尝试将项目放入队列，如果队列已满，则阻塞等待
                work_queue.put(item, timeout=2) # 设置超时，避免无限等待
                print(f"生产者 {self.name} 生产了: {item}, 队列大小: {work_queue.qsize()}")
                time.sleep(random.random() * 0.5) # 模拟生产时间
            except queue.Full:
                print(f"生产者 {self.name} 发现队列已满，暂停生产")
                time.sleep(1)
        # 发送结束信号 (None 通常用作结束标志)
        work_queue.put(None)
        print(f"生产者 {self.name} 生产结束.")

class Consumer(threading.Thread):
    """消费者线程"""
    def run(self):
        print(f"消费者 {self.name} 启动...")
        while True:
            try:
                # 尝试从队列获取项目，如果队列为空，则阻塞等待
                item = work_queue.get(timeout=3) # 设置超时
                if item is None: # 收到结束信号
                    print(f"消费者 {self.name} 收到结束信号，退出.")
                    work_queue.task_done() # 标记任务完成
                    # 将 None 重新放回，以便其他消费者也能收到结束信号
                    work_queue.put(None)
                    break
                print(f"消费者 {self.name} 消费了: {item}, 队列大小: {work_queue.qsize()}")
                time.sleep(random.random() * 1.0) # 模拟消费时间
                work_queue.task_done() # 标记队列中的一个任务已完成
            except queue.Empty:
                print(f"消费者 {self.name} 发现队列为空，等待生产...")
                # 如果超时仍为空，可能生产者已结束且队列已空
                # 检查生产者是否还在活动，或者是否有其他方式判断结束
                # 这里简单处理，如果队列为空且超时，也认为可以结束
                # (更健壮的方式需要更复杂的逻辑或信号)
                # 但由于生产者会放 None，理论上不会一直 Empty 超时
                pass # 继续循环等待

# 创建并启动生产者和消费者线程
producer_thread = Producer(name="P1")
consumer_thread1 = Consumer(name="C1")
consumer_thread2 = Consumer(name="C2") # 可以有多个消费者

producer_thread.start()
consumer_thread1.start()
consumer_thread2.start()

# 等待所有线程结束
producer_thread.join()
consumer_thread1.join()
consumer_thread2.join()

print("生产者消费者模型演示结束.\n")

# --- 2. 多线程基础 --- 
print("--- 2. 多线程基础示例 ---")

def simple_worker(worker_id, duration):
    """简单的线程工作函数"""
    print(f"线程 {worker_id} 开始工作，将执行 {duration} 秒")
    time.sleep(duration)
    print(f"线程 {worker_id} 工作结束")

# 创建线程列表
threads = []

# 创建多个线程
for i in range(3):
    # 创建 Thread 对象，指定目标函数和参数
    t = threading.Thread(target=simple_worker, args=(i, random.randint(1, 3)))
    threads.append(t)
    # 启动线程
    t.start()
    print(f"启动了线程 {i}")

# 等待所有线程完成
print("主线程等待所有子线程完成...")
for t in threads:
    t.join() # join() 会阻塞主线程，直到被调用的线程执行完毕

print("所有子线程执行完毕，主线程继续执行.")

# 继承 Thread 类创建线程
class MyThread(threading.Thread):
    def __init__(self, name, delay):
        threading.Thread.__init__(self)
        self.name = name
        self.delay = delay

    def run(self):
        print(f"启动线程 (继承方式): {self.name}")
        time.sleep(self.delay)
        print(f"退出线程 (继承方式): {self.name}")

# 创建并启动继承方式的线程
thread1 = MyThread("Thread-A", 1)
thread2 = MyThread("Thread-B", 2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("继承方式的线程执行完毕.")

print("\n第9节示例代码结束。")