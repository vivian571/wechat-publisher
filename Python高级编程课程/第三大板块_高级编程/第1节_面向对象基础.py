# 第1节: 面向对象基础
# 内容: 面向对象思维、类、对象、__init__方法

# --- 面向对象思维 --- 
# 面向对象编程 (OOP) 是一种编程范式，它使用“对象”来设计软件。
# 对象具有 状态 (属性/变量) 和 行为 (方法/函数)。
# 核心思想: 将数据和操作数据的函数封装在一起。

# --- 类的定义 --- 
# 类是创建对象的蓝图或模板。
# 使用 `class` 关键字定义一个类。

class Dog:
    """这是一个表示狗的简单类"""
    
    # 类变量 (所有实例共享)
    species = "犬科"

    # --- __init__ 方法 (构造函数) ---
    # 特殊方法，在创建对象(实例)时自动调用。
    # 用于初始化对象的状态 (实例变量)。
    # `self` 参数代表正在创建的对象实例。
    def __init__(self, name, age):
        print(f"创建一只新的狗: {name}")
        # 实例变量 (每个实例独有)
        self.name = name  
        self.age = age

    # --- 实例方法 ---
    # 类中定义的函数，第一个参数通常是 `self`。
    # 用于定义对象的行为。
    def bark(self):
        print(f"{self.name} 发出了汪汪叫声!")

    def describe(self):
        return f"{self.name} 是一只 {self.age} 岁的{self.species}。"

# --- 创建对象 (实例化) --- 
# 通过调用类名并传递 __init__ 方法所需的参数来创建类的实例。

print("--- 创建第一个 Dog 对象 ---")
my_dog = Dog("旺财", 3) # 调用 Dog 类，会自动执行 __init__ 方法

print("--- 创建第二个 Dog 对象 ---")
another_dog = Dog("小白", 1)

# --- 访问对象的属性和方法 --- 
# 使用点 (.) 操作符访问对象的属性和调用其方法。

print("\n--- 访问对象属性 ---")
print(f"第一只狗的名字: {my_dog.name}") # 输出: 旺财
print(f"第二只狗的年龄: {another_dog.age}") # 输出: 1
print(f"所有狗的种类: {Dog.species}") # 可以通过类名访问类变量
print(f"旺财的种类: {my_dog.species}") # 也可以通过实例访问类变量

print("\n--- 调用对象方法 ---")
my_dog.bark() # 输出: 旺财 发出了汪汪叫声!
another_dog.bark()

description = my_dog.describe()
print(description) # 输出: 旺财 是一只 3 岁的犬科。

print("\n第1节示例代码结束。")