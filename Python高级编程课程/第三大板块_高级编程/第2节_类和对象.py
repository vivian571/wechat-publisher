# 第2节: 类和对象
# 内容: 类与对象属性关系、绑定与非绑定方法、继承

# --- 类属性 vs 实例属性 ---
# 类属性: 属于类本身，所有实例共享。
# 实例属性: 属于类的实例，每个实例独有，通常在 __init__ 中定义。

class Item:
    # 类属性
    tax_rate = 0.1 # 假设税率为10%
    all_items = [] # 用于追踪所有创建的 Item 实例

    def __init__(self, name: str, price: float):
        # 实例属性
        self.name = name
        self.price = price
        print(f"创建物品: {self.name}, 价格: {self.price}")
        # 将新创建的实例添加到类属性列表中
        Item.all_items.append(self)

    def calculate_total_price(self) -> float:
        """计算包含税的价格"""
        return self.price * (1 + self.tax_rate) # 实例可以访问类属性

print("--- 类属性与实例属性示例 ---")
item1 = Item("笔记本", 5.0)
item2 = Item("钢笔", 1.5)

print(f"{item1.name} 的总价: {item1.calculate_total_price()}")
print(f"{item2.name} 的总价: {item2.calculate_total_price()}")

# 访问类属性
print(f"税率: {Item.tax_rate}")
print(f"所有物品实例数量: {len(Item.all_items)}")
for item in Item.all_items:
    print(f"  - {item.name}")

# 修改类属性会影响所有实例 (如果实例没有覆盖该属性)
# Item.tax_rate = 0.15
# print(f"修改税率后，{item1.name} 的总价: {item1.calculate_total_price()}")

# --- 绑定方法 vs 非绑定方法 (静态方法和类方法) ---

class Calculator:
    def __init__(self, value=0):
        self.value = value # 实例属性

    # 绑定方法 (实例方法)
    # 第一个参数是 self，与特定实例绑定
    def add(self, x):
        self.value += x
        print(f"实例 {id(self)} 调用 add, 当前值: {self.value}")

    # 类方法
    # 第一个参数是 cls (类本身)
    # 通常用于操作类属性或创建实例
    @classmethod
    def create_with_double(cls, value):
        print(f"类方法被调用，创建值为 {value*2} 的实例")
        return cls(value * 2)

    # 静态方法
    # 没有 self 或 cls 参数，与类或实例的状态无关
    # 像普通函数一样，但放在类的命名空间下
    @staticmethod
    def multiply(a, b):
        result = a * b
        print(f"静态方法 multiply({a}, {b}) = {result}")
        return result

print("\n--- 方法类型示例 ---")
calc1 = Calculator(10)
calc2 = Calculator(100)

# 调用绑定方法 (实例方法)
calc1.add(5)
calc2.add(10)

# 调用类方法 (通过类或实例调用)
calc3 = Calculator.create_with_double(25)
print(f"通过类方法创建的实例 calc3 的值: {calc3.value}")
calc4 = calc1.create_with_double(3) # 也可以通过实例调用类方法
print(f"通过实例调用类方法创建的 calc4 的值: {calc4.value}")

# 调用静态方法 (通过类或实例调用)
product1 = Calculator.multiply(6, 7)
product2 = calc1.multiply(3, 4) # 也可以通过实例调用静态方法

# --- 继承 --- 
# 继承允许一个类 (子类/派生类) 获取另一个类 (父类/基类) 的属性和方法。
# 这有助于代码重用和创建层次结构。

class Animal:
    """动物基类"""
    def __init__(self, name):
        self.name = name
        print(f"创建动物: {self.name}")

    def speak(self):
        # raise NotImplementedError("子类必须实现此方法")
        print(f"{self.name} 发出声音 (来自 Animal 类)")

class Cat(Animal): # Cat 继承自 Animal
    """猫类，继承自动物类"""
    def __init__(self, name, color):
        # 调用父类的 __init__ 方法来初始化 name
        super().__init__(name)
        self.color = color # 添加 Cat 特有的属性
        print(f"{self.name} 是一只 {self.color} 的猫")

    # 重写 (Override) 父类的方法
    def speak(self):
        print(f"{self.name} 发出喵喵叫! (来自 Cat 类)")

    def purr(self): # Cat 特有的方法
        print(f"{self.name} 发出咕噜咕噜声。")

print("\n--- 继承示例 ---")
animal = Animal("普通动物")
animal.speak()

my_cat = Cat("咪咪", "橘色")
my_cat.speak() # 调用 Cat 类重写后的 speak 方法
my_cat.purr()  # 调用 Cat 类特有的方法

print(f"{my_cat.name} 是 Animal 的实例吗? {isinstance(my_cat, Animal)}") # True
print(f"{my_cat.name} 是 Cat 的实例吗? {isinstance(my_cat, Cat)}")     # True
print(f"{animal.name} 是 Cat 的实例吗? {isinstance(animal, Cat)}")     # False

print("\n第2节示例代码结束。")