# 第11节: 协程
# 内容: 回调机制、协程理论与实现方案

import asyncio
import time

# --- 1. 回调机制示例 --- 
print("--- 1. 回调机制示例 ---")

def long_running_task(callback):
    """模拟一个耗时操作，完成后调用回调函数"""
    print("开始执行耗时任务...")
    time.sleep(2) # 模拟耗时
    result = "任务完成，结果数据"
    print("耗时任务结束.")
    callback(result) # 调用回调函数并传递结果

def handle_result(data):
    """回调函数，处理任务结果"""
    print(f"回调函数被调用，接收到数据: {data}")

print("启动耗时任务...")
long_running_task(handle_result)
print("主程序继续执行其他操作...")
print("回调机制示例结束。\n")

# --- 2. 协程基础 (asyncio) --- 
print("--- 2. 协程基础 (asyncio) 示例 ---")

async def simple_coroutine(name, delay):
    """一个简单的协程函数"""
    print(f"协程 {name}: 开始执行，将等待 {delay} 秒")
    await asyncio.sleep(delay) # await 挂起协程，让出控制权
    print(f"协程 {name}: 等待结束，恢复执行")
    return f"协程 {name} 完成"

async def main_async():
    """主异步函数，用于运行协程"""
    print("主异步函数开始")
    
    # 创建多个协程任务
    task1 = asyncio.create_task(simple_coroutine("A", 2))
    task2 = asyncio.create_task(simple_coroutine("B", 1))
    
    print("协程任务已创建，等待它们完成...")
    
    # 等待协程任务完成并获取结果
    # asyncio.gather 按顺序收集结果
    results = await asyncio.gather(task1, task2)
    
    print("所有协程任务已完成")
    for result in results:
        print(f"获取到结果: {result}")
        
    print("主异步函数结束")

# 运行主异步函数
# 在 Python 3.7+ 中，可以直接使用 asyncio.run()
print("运行 asyncio 事件循环...")
asyncio.run(main_async())
print("asyncio 事件循环结束。\n")

# --- 3. 协程与 Future/Task --- 
print("--- 3. 协程与 Future/Task 示例 ---")

async def another_coroutine():
    print("另一个协程：开始")
    await asyncio.sleep(1.5)
    print("另一个协程：结束")
    return 42

async def run_with_future():
    print("使用 Future/Task 运行协程")
    # asyncio.create_task() 返回一个 Task 对象，它是 Future 的子类
    task = asyncio.create_task(another_coroutine())
    
    print(f"Task 已创建，状态: {task.done()}")
    
    # 可以添加回调函数，在 Task 完成时自动调用
    def task_callback(future):
        print(f"Task 回调: 任务完成，结果: {future.result()}, 异常: {future.exception()}")
        
    task.add_done_callback(task_callback)
    
    # 等待 Task 完成
    result = await task
    print(f"Task 完成后获取结果: {result}")
    print(f"Task 完成后状态: {task.done()}")

asyncio.run(run_with_future())
print("协程与 Future/Task 示例结束。\n")

print("\n第11节示例代码结束。")