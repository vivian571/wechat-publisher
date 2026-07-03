# 第4节: 多态和封装基础
# 内容: 组合扩展、多态、魔法方法、封装

# --- 多态 (Polymorphism) --- 
# 多态意味着 "多种形态"。
# 在 OOP 中，指不同类的对象可以响应相同的方法调用。
# Python 通过 "鸭子类型 (Duck Typing)" 来实现多态："如果它走起路来像鸭子，叫起来也像鸭子，那它就是一只鸭子。"
# 关注对象的行为 (方法) 而不是它的类型。

print("--- 多态示例 (鸭子类型) ---")

class Cat:
    def speak(self):
        print("喵喵!")

class Dog:
    def speak(self):
        print("汪汪!")

class Duck:
    def speak(self):
        print("嘎嘎!")

# 这个函数接受任何有 speak 方法的对象
def make_animal_speak(animal):
    animal.speak() # 不关心 animal 的具体类型，只要它有 speak 方法

# 创建不同类型的对象
cat = Cat()
dog = Dog()
duck = Duck()

# 调用同一个函数，传入不同类型的对象
print("让猫叫:")
make_animal_speak(cat)
print("让狗叫:")
make_animal_speak(dog)
print("让鸭子叫:")
make_animal_speak(duck)

# --- 封装 (Encapsulation) 基础 --- 
# 封装是将数据 (属性) 和操作数据的方法捆绑在一起的过程。
# 目的是隐藏对象的内部状态和实现细节，只暴露必要的接口。
# Python 没有像 Java/C++ 那样的严格的 private/protected 关键字，主要依靠命名约定。

print("\n--- 封装示例 --- ")

class BankAccount:
    def __init__(self, account_holder, initial_balance=0):
        self.account_holder = account_holder # 公开属性
        # 使用单下划线 `_` 约定为 "受保护" 属性
        # 意味着它不应该在类外部直接访问，但 Python 不会强制阻止
        self._balance = initial_balance 
        # 使用双下划线 `__` 开头的属性会触发 "名称改写 (Name Mangling)"
        # Python 会将其名称改为 `_ClassName__attributeName`，使其更难从外部直接访问
        self.__transaction_log = [] 
        print(f"账户为 {self.account_holder} 创建，初始余额: {self._balance}")

    # 提供公共方法来间接访问和修改 "受保护" 或 "私有" 属性
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            self.__add_log(f"存入: {amount}")
            print(f"成功存入 {amount}，当前余额: {self._balance}")
        else:
            print("存款金额必须大于 0")

    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            self.__add_log(f"取出: {amount}")
            print(f"成功取出 {amount}，当前余额: {self._balance}")
        elif amount > self._balance:
            print("余额不足")
        else:
            print("取款金额必须大于 0")

    def get_balance(self):
        """提供一个公共方法来获取余额"""
        self.__add_log("查询余额")
        return self._balance

    # "私有" 方法，通常用于类的内部实现
    def __add_log(self, entry):
        # 可以在这里添加时间戳等
        self.__transaction_log.append(entry)
        # print(f"内部日志: {entry}") # 内部可以访问

    def get_transaction_log(self):
        """提供公共方法访问日志"""
        return self.__transaction_log

# 创建账户实例
account = BankAccount("张三", 1000)

# 使用公共方法进行操作
account.deposit(500)
account.withdraw(200)

# 通过公共方法获取余额
current_balance = account.get_balance()
print(f"张三的当前余额: {current_balance}")

# 尝试直接访问属性
print(f"账户持有人: {account.account_holder}") # 公开属性，可以直接访问

# 尝试访问 "受保护" 属性 (不推荐，但可以做到)
# print(f"直接访问余额 (不推荐): {account._balance}") 

# 尝试直接访问 "私有" 属性 (会失败)
try:
    print(account.__balance) # 这会报错 AttributeError
except AttributeError as e:
    print(f"尝试直接访问 __balance 失败: {e}")

try:
    print(account.__transaction_log) # 这也会报错 AttributeError
except AttributeError as e:
    print(f"尝试直接访问 __transaction_log 失败: {e}")

# 可以通过名称改写后的名字访问 (非常不推荐，破坏封装)
# print(f"通过名称改写访问日志 (非常不推荐): {account._BankAccount__transaction_log}")

# 通过公共方法获取日志
log = account.get_transaction_log()
print(f"交易日志: {log}")

print("\n第4节示例代码结束。")