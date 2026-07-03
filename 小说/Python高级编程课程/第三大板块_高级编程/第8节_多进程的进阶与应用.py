# 第8节: 多进程的进阶与应用
# 内容: 进程隔离、互斥锁、信号量、消息队列

import multiprocessing
import time
import os

# --- 1. 进程隔离 --- 
# 每个进程都有自己独立的内存空间，变量不共享
print("--- 1. 进程隔离示例 ---")

global_list = []

def worker_process_isolation(num):
    """子进程函数，尝试修改全局列表"""
    print(f"子进程 {os.getpid()} 开始，尝试添加 {num} 到列表")
    # 在子进程中修改 global_list，但这不会影响父进程中的 global_list
    global_list.append(num)
    print(f"子进程 {os.getpid()} 中的 global_list: {global_list}")

if __name__ == "__main__": # Windows下多进程必须在 if __name__ == "__main__": 下启动
    p = multiprocessing.Process(target=worker_process_isolation, args=(1,))
    p.start()
    p.join() # 等待子进程结束

    print(f"父进程 {os.getpid()} 中的 global_list: {global_list}") # 父进程的列表仍然是空的
    print("可以看到，子进程对全局变量的修改不会影响父进程，体现了进程隔离。\n")

# --- 2. 互斥锁 (Lock) --- 
# 确保同一时间只有一个进程可以访问共享资源
print("--- 2. 互斥锁 (Lock) 示例 ---")

def worker_with_lock(lock, counter):
    """带锁的子进程函数"""
    for _ in range(5):
        lock.acquire() # 获取锁
        try:
            # 访问共享资源 (模拟)
            current_value = counter.value
            print(f"进程 {os.getpid()} 获取锁，当前 counter: {current_value}")
            time.sleep(0.1) # 模拟耗时操作
            counter.value += 1
            print(f"进程 {os.getpid()} 修改后 counter: {counter.value}")
        finally:
            lock.release() # 释放锁
        time.sleep(0.05) # 给其他进程机会获取锁

if __name__ == "__main__":
    lock = multiprocessing.Lock()
    # 使用 Value 创建共享内存中的整数
    counter = multiprocessing.Value('i', 0) # 'i' 表示 integer 类型，初始值为 0

    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=worker_with_lock, args=(lock, counter))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"\n所有进程执行完毕，最终 counter 值: {counter.value}")
    print("使用互斥锁确保了 counter 的值被正确地增加了 3 * 5 = 15 次。\n")

# --- 3. 信号量 (Semaphore) --- 
# 控制同时访问特定资源或执行特定代码段的进程数量
print("--- 3. 信号量 (Semaphore) 示例 ---")

def worker_with_semaphore(semaphore, worker_id):
    """带信号量的子进程函数"""
    print(f"进程 {worker_id} ({os.getpid()}) 尝试获取信号量...")
    with semaphore: # 使用 with 语句自动管理 acquire 和 release
        print(f"进程 {worker_id} ({os.getpid()}) 获取了信号量，开始工作...")
        time.sleep(2) # 模拟工作
        print(f"进程 {worker_id} ({os.getpid()}) 工作完成，释放信号量。")

if __name__ == "__main__":
    # 创建一个信号量，允许最多 2 个进程同时访问
    semaphore = multiprocessing.Semaphore(2)

    processes = []
    for i in range(5): # 创建 5 个进程
        p = multiprocessing.Process(target=worker_with_semaphore, args=(semaphore, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("\n所有进程执行完毕。可以看到，同时只有最多 2 个进程在 '工作'。\n")

# --- 4. 消息队列 (Queue) --- 
# 实现进程间的数据安全交换
print("--- 4. 消息队列 (Queue) 示例 ---")

def producer(queue):
    """生产者进程"""
    print(f"生产者 {os.getpid()} 开始生产数据...")
    for i in range(5):
        item = f"数据 {i}"
        print(f"生产者 {os.getpid()} 生产了: {item}")
        queue.put(item)
        time.sleep(0.5)
    queue.put(None) # 发送结束信号
    print(f"生产者 {os.getpid()} 生产结束。")

def consumer(queue):
    """消费者进程"""
    print(f"消费者 {os.getpid()} 开始等待消费...")
    while True:
        item = queue.get() # 阻塞等待，直到队列中有数据
        if item is None: # 收到结束信号
            print(f"消费者 {os.getpid()} 收到结束信号，退出。")
            break
        print(f"消费者 {os.getpid()} 消费了: {item}")
        time.sleep(1) # 模拟消费处理时间

if __name__ == "__main__":
    # 创建一个进程安全的队列
    queue = multiprocessing.Queue()

    # 创建并启动生产者和消费者进程
    p_producer = multiprocessing.Process(target=producer, args=(queue,))
    p_consumer = multiprocessing.Process(target=consumer, args=(queue,))

    p_producer.start()
    p_consumer.start()

    # 等待进程结束
    p_producer.join()
    p_consumer.join()

    print("\n生产者和消费者进程执行完毕。消息队列实现了进程间的数据传递。")

print("\n第8节示例代码结束。")