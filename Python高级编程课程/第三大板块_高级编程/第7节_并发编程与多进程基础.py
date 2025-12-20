# 第7节: 并发编程与多进程基础
# 内容: 并发理论、进程、join方法

# --- 并发 vs 并行 ---
# 并发 (Concurrency): 指系统能够处理多个任务的能力，但不一定同时执行。在单核 CPU 上，通过快速切换任务实现并发。
# 并行 (Parallelism): 指系统能够同时执行多个任务。通常需要多核 CPU 才能实现真正的并行。
# Python 的全局解释器锁 (GIL) 限制了同一时刻只有一个线程能执行 Python 字节码，因此 Python 的多线程更适合 I/O 密集型任务 (实现并发)。
# 对于 CPU 密集型任务，为了实现并行，通常使用多进程。

# --- 多进程基础 (multiprocessing) ---
# `multiprocessing` 模块允许创建和管理进程，可以利用多核 CPU 实现真正的并行计算。
# 每个进程有自己独立的内存空间，数据不共享 (需要特殊机制如 Queue, Pipe 进行通信)。

import multiprocessing
import time
import os

print("--- 多进程基础示例 ---")

# --- 定义一个进程要执行的任务函数 ---
def worker_task(name, duration):
    """一个简单的任务函数，模拟耗时操作"""
    print(f"进程 {name} (PID: {os.getpid()}) 开始执行...")
    time.sleep(duration)
    print(f"进程 {name} (PID: {os.getpid()}) 执行完毕，耗时 {duration} 秒。")

# --- 创建和启动进程 ---
if __name__ == '__main__': # 在 Windows 上创建子进程必须在 if __name__ == '__main__': 块中
    print(f"主进程 (PID: {os.getpid()}) 开始执行...")

    # 1. 创建 Process 对象
    # target: 指定进程要执行的函数
    # args: 以元组形式传递给目标函数的参数
    # kwargs: 以字典形式传递给目标函数的关键字参数
    process1 = multiprocessing.Process(target=worker_task, args=("任务A", 2))
    process2 = multiprocessing.Process(target=worker_task, kwargs={"name": "任务B", "duration": 3})

    print("\n准备启动子进程...")

    # 2. 启动进程
    # 调用 start() 方法后，子进程会在后台开始执行 target 函数
    start_time = time.time()
    process1.start()
    process2.start()

    print("子进程已启动，主进程继续执行其他任务...")
    # 主进程可以继续做其他事情，而子进程在后台运行
    # time.sleep(1)
    # print("主进程做了一些其他事情...")

    # --- 等待子进程结束 (join) ---
    # 调用 join() 方法会阻塞主进程，直到该子进程执行完毕。
    # 如果不调用 join()，主进程可能会在子进程完成前就结束了。
    print("\n主进程等待子进程完成...")
    process1.join() # 等待 process1 结束
    print("进程 任务A 已完成。")
    process2.join() # 等待 process2 结束
    print("进程 任务B 已完成。")

    end_time = time.time()
    print(f"\n所有子进程执行完毕，主进程结束。总耗时: {end_time - start_time:.2f} 秒")
    # 注意：总耗时约等于耗时最长的子进程的时间 (3秒)，而不是所有子进程时间之和 (2+3=5秒)，体现了并行/并发的效果。

    # --- 进程的其他属性和方法 ---
    print("\n--- 进程属性示例 ---")
    # 创建一个新进程但不立即启动，用于演示
    process3 = multiprocessing.Process(target=worker_task, args=("任务C", 1))
    print(f"进程 任务C 的名称: {process3.name}") # 默认名称 Process-N
    print(f"进程 任务C 的 PID (启动前): {process3.pid}") # 启动前为 None
    print(f"进程 任务C 是否存活 (启动前): {process3.is_alive()}") # False

    # process3.start()
    # print(f"进程 任务C 的 PID (启动后): {process3.pid}")
    # time.sleep(0.1) # 给点时间让进程启动
    # print(f"进程 任务C 是否存活 (运行中): {process3.is_alive()}") # True
    # process3.join()
    # print(f"进程 任务C 是否存活 (结束后): {process3.is_alive()}") # False
    # print(f"进程 任务C 的退出码: {process3.exitcode}") # 正常结束为 0

    # process3.terminate() # 强制终止进程 (不推荐，可能导致资源未释放)

print("\n第7节示例代码结束。")