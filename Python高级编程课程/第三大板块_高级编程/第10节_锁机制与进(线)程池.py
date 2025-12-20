# 第10节: 锁机制与进(线)程池
# 内容: 死锁、递归锁、定时器、进程池

import threading
import time
import multiprocessing
import os

# --- 1. 死锁 (Deadlock) 示例 ---
print("--- 1. 死锁示例 ---")

# 创建两个锁
lock_a = threading.Lock()
lock_b = threading.Lock()

def worker_a():
    print("Worker A: 尝试获取 lock_a...")
    lock_a.acquire()
    print("Worker A: 已获取 lock_a，暂停1秒...")
    time.sleep(1)
    print("Worker A: 尝试获取 lock_b...")
    lock_b.acquire()
    print("Worker A: 已获取 lock_b") # 这行通常不会执行
    lock_b.release()
    lock_a.release()
    print("Worker A: 释放了所有锁")

def worker_b():
    print("Worker B: 尝试获取 lock_b...")
    lock_b.acquire()
    print("Worker B: 已获取 lock_b，暂停1秒...")
    time.sleep(1)
    print("Worker B: 尝试获取 lock_a...")
    lock_a.acquire()
    print("Worker B: 已获取 lock_a") # 这行通常不会执行
    lock_a.release()
    lock_b.release()
    print("Worker B: 释放了所有锁")

# 创建并启动线程
thread_a = threading.Thread(target=worker_a)
thread_b = threading.Thread(target=worker_b)

print("启动死锁演示线程...")
thread_a.start()
thread_b.start()

# 等待线程结束 (这里会永远等待，因为发生了死锁)
# thread_a.join()
# thread_b.join()
print("死锁演示：线程 A 持有 lock_a 等待 lock_b，线程 B 持有 lock_b 等待 lock_a，互相等待导致死锁。")
print("程序将卡住，需要手动停止。\n")
# 为了让后续代码能执行，我们不等这两个线程了
time.sleep(3) # 等待足够时间让死锁发生并打印信息
print("死锁演示部分结束（未 join 线程以继续）。\n")


# --- 2. 递归锁 (RLock) --- 
# 允许同一个线程多次获取同一个锁，而不会造成死锁
print("--- 2. 递归锁 (RLock) 示例 ---")

recursive_lock = threading.RLock() # 创建递归锁

def recursive_function(level):
    print(f"层级 {level}: 尝试获取递归锁...")
    recursive_lock.acquire()
    print(f"层级 {level}: 已获取递归锁 (第 {recursive_lock._is_owned()} 次)")
    try:
        if level > 0:
            print(f"层级 {level}: 调用下一层...")
            recursive_function(level - 1)
        else:
            print(f"层级 {level}: 到达最底层")
        time.sleep(0.5)
    finally:
        print(f"层级 {level}: 释放递归锁...")
        recursive_lock.release()
        print(f"层级 {level}: 已释放递归锁")

# 在一个新线程中运行递归函数
recursive_thread = threading.Thread(target=recursive_function, args=(3,))
recursive_thread.start()
recursive_thread.join()

print("递归锁演示结束。可以看到同一线程可以多次获取 RLock 而不阻塞。\n")


# --- 3. 定时器 (Timer) --- 
# 在指定延迟后执行一个函数
print("--- 3. 定时器 (Timer) 示例 ---")

def timed_task(message):
    print(f"定时任务执行: {message} (时间: {time.strftime('%X')})")

print(f"主线程: 准备启动一个 3 秒后的定时任务 (当前时间: {time.strftime('%X')})")
# 创建一个 Timer 对象，3秒后执行 timed_task 函数，并传递参数
timer = threading.Timer(3.0, timed_task, args=("Hello from Timer!",))
timer.start() # 启动定时器

print("主线程: 定时器已启动，主线程继续执行其他任务...")
# 主线程可以继续做其他事情
time.sleep(1)
print("主线程: 正在执行...")
time.sleep(3) # 等待足够时间让定时器任务执行

# 如果需要，可以取消定时器 (在 start 之后，任务执行之前)
# timer.cancel()
# print("定时器已被取消")

print("定时器演示结束。\n")


# --- 4. 进程池 (Pool) --- 
# 管理一组工作进程，方便地将任务分配给它们
print("--- 4. 进程池 (Pool) 示例 ---")

def worker_task(x):
    """进程池工作函数，模拟耗时计算任务"""
    # 获取当前进程ID
    pid = os.getpid()
    # 模拟耗时操作
    time.sleep(1)
    # 返回计算结果
    result = x * x
    return f"进程 {pid} 计算 {x} 的平方为: {result}"
