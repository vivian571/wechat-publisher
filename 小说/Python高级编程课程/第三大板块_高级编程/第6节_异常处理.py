# 第6节: 异常处理
# 内容: 异常分析、购物车案例设计

# --- 异常处理基础 (try...except) ---
# 当代码可能引发错误时，使用 try 块将其包围。
# 如果 try 块中的代码引发异常，程序会跳转到匹配的 except 块。

print("--- 异常处理基础 ---")

try:
    numerator = 10
    denominator = 0
    result = numerator / denominator # 这将引发 ZeroDivisionError
    print(f"计算结果: {result}") # 这行不会执行
except ZeroDivisionError:
    print("错误：尝试除以零！")

print("程序继续执行...")

# --- 捕获特定类型的异常 ---
# 可以有多个 except 块来处理不同类型的异常。

print("\n--- 捕获特定异常 ---")

try:
    my_list = [1, 2, 3]
    index = 5
    value = my_list[index] # 这将引发 IndexError
    print(f"索引 {index} 处的值: {value}")
except IndexError:
    print(f"错误：索引 {index} 超出列表范围！")
except TypeError:
    print("错误：发生了类型错误！")
except Exception as e: # 捕获所有其他类型的异常 (Exception 是大多数内置异常的基类)
    print(f"发生了未知错误: {e}")
    print(f"错误类型: {type(e)}")

# --- try...except...else ---
# else 块中的代码仅在 try 块没有引发任何异常时执行。

print("\n--- try...except...else 示例 ---")

try:
    num_str = "123"
    num_int = int(num_str) # 尝试转换
except ValueError:
    print(f"错误：无法将 '{num_str}' 转换为整数。")
else:
    print(f"成功将 '{num_str}' 转换为整数: {num_int}")
    # 可以在这里执行依赖于成功转换的操作

# --- try...except...finally ---
# finally 块中的代码无论是否发生异常，总会被执行。
# 通常用于资源清理，如关闭文件或网络连接。

print("\n--- try...except...finally 示例 ---")

file = None
try:
    file = open("non_existent_file.txt", "r") # 尝试打开不存在的文件，引发 FileNotFoundError
    content = file.read()
    print("文件内容读取成功:")
    print(content)
except FileNotFoundError:
    print("错误：文件未找到！")
except Exception as e:
    print(f"读取文件时发生错误: {e}")
finally:
    if file:
        file.close()
        print("文件已关闭 (在 finally 块中)。")
    else:
        print("文件未能成功打开，无需关闭 (在 finally 块中)。")

# --- 主动抛出异常 (raise) ---
# 可以使用 raise 语句手动引发一个异常。

print("\n--- 主动抛出异常 (raise) --- ")

def check_age(age):
    if age < 0:
        raise ValueError("年龄不能为负数！")
    elif age < 18:
        raise Exception("未成年人禁止访问！") # 可以抛出通用 Exception
    else:
        print("年龄检查通过。")

try:
    check_age(25)
    check_age(15)
    # check_age(-5) # 取消注释会引发 ValueError
except ValueError as ve:
    print(f"捕获到 ValueError: {ve}")
except Exception as e:
    print(f"捕获到其他异常: {e}")

# --- 自定义异常 --- 
# 可以通过继承 Exception 类或其子类来创建自己的异常类型。

print("\n--- 自定义异常 --- ")

class InsufficientFundsError(Exception):
    """自定义异常，表示账户余额不足"""
    def __init__(self, current_balance, requested_amount):
        self.current_balance = current_balance
        self.requested_amount = requested_amount
        message = f"取款失败：当前余额 {current_balance}，请求金额 {requested_amount}"
        super().__init__(message) # 调用父类的构造函数

def withdraw_from_account(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    else:
        print(f"成功取出 {amount}，剩余余额 {balance - amount}")
        return balance - amount

try:
    account_balance = 100
    withdraw_from_account(account_balance, 50)
    withdraw_from_account(account_balance, 150) # 这将引发 InsufficientFundsError
except InsufficientFundsError as ife:
    print(f"捕获到自定义异常: {ife}")
    print(f"  - 当前余额: {ife.current_balance}")
    print(f"  - 请求金额: {ife.requested_amount}")

print("\n第6节示例代码结束。")