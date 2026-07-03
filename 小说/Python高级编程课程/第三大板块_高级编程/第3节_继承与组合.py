# 第3节: 继承与组合
# 内容: 单继承、多继承、重用父类功能方式、组合

# --- 继承 (Inheritance) 深入 --- 
# 继承是一种 "is-a" (是一个) 的关系。
# 子类继承父类的属性和方法，可以添加新功能或重写现有功能。

print("--- 继承深入示例 ---")

class Employee:
    """员工基类"""
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        print(f"创建员工: {self.name}, 薪水: {self.salary}")

    def work(self):
        print(f"{self.name} 正在努力工作。")

    def get_details(self):
        return f"姓名: {self.name}, 薪水: {self.salary}"

class Manager(Employee): # Manager 继承自 Employee
    """经理类，继承自员工类"""
    def __init__(self, name, salary, department):
        super().__init__(name, salary) # 调用父类的 __init__
        self.department = department # 添加经理特有的属性
        print(f"{self.name} 被分配到 {self.department} 部门。")

    # 重写 (Override) 父类的 work 方法
    def work(self):
        print(f"{self.name} 正在管理 {self.department} 部门。")

    # 添加经理特有的方法
    def approve_leave(self, employee_name):
        print(f"经理 {self.name} 批准了 {employee_name} 的假期。")

    # 扩展父类方法 (调用父类方法 + 添加新功能)
    def get_details(self):
        base_details = super().get_details() # 调用父类的 get_details
        return f"{base_details}, 部门: {self.department}"

class Director(Manager): # Director 继承自 Manager (多层继承)
    """总监类，继承自经理类"""
    def __init__(self, name, salary, department, region):
        super().__init__(name, salary, department)
        self.region = region
        print(f"{self.name} 负责 {self.region} 区域。")

    # 重写 work 方法
    def work(self):
        print(f"总监 {self.name} 正在制定 {self.region} 区域的战略。")

    # 添加总监特有的方法
    def conduct_meeting(self):
        print(f"总监 {self.name} 正在主持区域会议。")

# 创建实例
emp = Employee("张三", 5000)
mgr = Manager("李四", 10000, "技术部")
dir = Director("王五", 20000, "技术部", "华东")

print("\n--- 调用方法 ---")
emp.work()
mgr.work()
dir.work()

print("\n--- 获取详情 ---")
print(emp.get_details())
print(mgr.get_details())
print(dir.get_details())

print("\n--- 调用特定方法 ---")
mgr.approve_leave("小明")
dir.conduct_meeting()
dir.approve_leave("小红") # Director 继承了 Manager 的方法

# --- 组合 (Composition) --- 
# 组合是一种 "has-a" (有一个) 的关系。
# 一个类包含另一个类的实例作为其属性。
# 相比继承，组合通常更灵活，耦合度更低。

print("\n--- 组合示例 ---")

class Engine:
    """引擎类"""
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        print(f"引擎启动，马力: {self.horsepower}")

    def stop(self):
        print("引擎停止。")

class Wheel:
    """轮子类"""
    def __init__(self, size):
        self.size = size

    def rotate(self):
        print(f"尺寸为 {self.size} 的轮子正在旋转。")

class Car:
    """汽车类，使用组合"""
    def __init__(self, make, model, engine_hp, wheel_size):
        self.make = make
        self.model = model
        # 组合：Car 类包含一个 Engine 实例和一个 Wheel 实例列表
        self.engine = Engine(engine_hp) 
        self.wheels = [Wheel(wheel_size) for _ in range(4)] # 假设有4个轮子
        print(f"制造了一辆 {self.make} {self.model}")

    def drive(self):
        print(f"驾驶 {self.make} {self.model}...")
        self.engine.start()
        for wheel in self.wheels:
            wheel.rotate()

    def park(self):
        print(f"停放 {self.make} {self.model}...")
        self.engine.stop()

# 创建实例
my_car = Car("Toyota", "Camry", 180, 17)

print("\n--- 使用组合的汽车 ---")
my_car.drive()
my_car.park()

# 访问组合的部件
print(f"我的车的引擎马力: {my_car.engine.horsepower}")
print(f"我的车的一个轮子尺寸: {my_car.wheels[0].size}")

# --- 继承 vs 组合 --- 
# - 继承 (is-a): 当一个类是另一个类的特殊类型时使用。代码重用性强，但耦合度高。
# - 组合 (has-a): 当一个类需要另一个类的功能，但不一定是其特殊类型时使用。更灵活，耦合度低。
# - 优先使用组合而不是继承，除非 "is-a" 关系非常明确。

print("\n第3节示例代码结束。")