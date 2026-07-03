# 第5节: 封装、反射和单例模式
# 内容: 封装进阶、反射机制、单例模式设计

# --- 封装进阶: 属性 (Properties) ---
# 使用 @property 装饰器可以将方法伪装成属性访问，提供更优雅的封装。
# 可以定义 getter, setter, deleter 方法来控制属性的访问、修改和删除。

print("--- 封装进阶: 属性 (Properties) ---")

class Temperature:
    def __init__(self, celsius):
        # 使用 "受保护" 属性存储实际值
        self._celsius = celsius

    @property
    def celsius(self):
        """摄氏温度的 getter"""
        print("获取摄氏温度")
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """摄氏温度的 setter，带验证"""
        print(f"设置摄氏温度为 {value}")
        if value < -273.15: # 绝对零度
            raise ValueError("温度不能低于绝对零度!")
        self._celsius = value

    @celsius.deleter
    def celsius(self):
        """摄氏温度的 deleter"""
        print("删除摄氏温度 (重置为 0)")
        self._celsius = 0 # 或者设置为 None

    @property
    def fahrenheit(self):
        """华氏温度的 getter (只读属性)"""
        # 这是一个计算属性，没有直接的 setter
        return (self._celsius * 9/5) + 32

# 创建实例
temp = Temperature(25)

# 像访问属性一样访问 getter
print(f"当前摄氏温度: {temp.celsius}")
print(f"当前华氏温度: {temp.fahrenheit}")

# 像给属性赋值一样调用 setter
temp.celsius = 30
print(f"更新后摄氏温度: {temp.celsius}")

# 尝试设置无效值
try:
    temp.celsius = -300
except ValueError as e:
    print(f"设置失败: {e}")

# 像删除属性一样调用 deleter
del temp.celsius
print(f"删除后摄氏温度: {temp.celsius}")

# 尝试设置只读属性 (会失败)
# try:
#     temp.fahrenheit = 100
# except AttributeError as e:
#     print(f"设置华氏温度失败: {e}")

# --- 反射 (Reflection) ---
# 反射是指程序在运行时能够检查、访问和修改自身状态或行为的能力。
# Python 提供了几个内置函数来实现反射：
# - hasattr(object, name): 检查对象是否有指定名称的属性或方法。
# - getattr(object, name[, default]): 获取对象指定名称的属性或方法的值。
# - setattr(object, name, value): 设置对象指定名称的属性的值。
# - delattr(object, name): 删除对象指定名称的属性。

print("\n--- 反射示例 ---")

class DynamicObject:
    def __init__(self):
        self.static_attr = "这是一个静态属性"

    def existing_method(self):
        print("这是一个已存在的方法")

dyn_obj = DynamicObject()

# 检查属性/方法是否存在 (hasattr)
print(f"对象是否有 'static_attr' 属性? {hasattr(dyn_obj, 'static_attr')}")
print(f"对象是否有 'dynamic_attr' 属性? {hasattr(dyn_obj, 'dynamic_attr')}")
print(f"对象是否有 'existing_method' 方法? {hasattr(dyn_obj, 'existing_method')}")
print(f"对象是否有 'non_existent_method' 方法? {hasattr(dyn_obj, 'non_existent_method')}")

# 获取属性/方法 (getattr)
static_value = getattr(dyn_obj, 'static_attr')
print(f"获取 'static_attr' 的值: {static_value}")

# 获取不存在的属性，提供默认值
default_value = getattr(dyn_obj, 'dynamic_attr', '默认值')
print(f"获取 'dynamic_attr' (不存在) 的值: {default_value}")

# 获取方法并调用
method_ref = getattr(dyn_obj, 'existing_method')
method_ref() # 调用获取到的方法

# 设置属性 (setattr)
setattr(dyn_obj, 'dynamic_attr', 123)
print(f"设置 'dynamic_attr' 后，对象是否有该属性? {hasattr(dyn_obj, 'dynamic_attr')}")
print(f"获取新设置的 'dynamic_attr' 的值: {getattr(dyn_obj, 'dynamic_attr')}")

# 动态添加方法 (虽然可以，但不常见，通常在元类中处理更复杂场景)
def new_method(self):
    print("这是一个动态添加的方法")
setattr(dyn_obj, 'added_method', new_method.__get__(dyn_obj, DynamicObject))
if hasattr(dyn_obj, 'added_method'):
    dyn_obj.added_method()

# 删除属性 (delattr)
delattr(dyn_obj, 'static_attr')
print(f"删除 'static_attr' 后，对象是否有该属性? {hasattr(dyn_obj, 'static_attr')}")

# --- 单例模式 (Singleton Pattern) ---
# 单例模式确保一个类只有一个实例，并提供一个全局访问点。
# 常用于配置管理、日志记录、数据库连接池等场景。

print("\n--- 单例模式示例 --- ")

# 方法一: 使用模块级别的变量 (Pythonic 方式)
# 在一个模块中定义实例，其他地方导入该模块即可获得唯一实例
# (示例见 config_manager.py, 这里用内部类模拟)

# 方法二: 使用装饰器
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, db_url):
        print(f"初始化数据库连接到: {db_url} (只应发生一次)")
        self.db_url = db_url
        # 模拟连接建立
        self.connection_id = id(self)

    def connect(self):
        print(f"使用连接 {self.connection_id} 连接到 {self.db_url}")

# 创建实例 (实际上是获取单例)
conn1 = DatabaseConnection("mysql://user:pass@host1/db")
conn2 = DatabaseConnection("mysql://user:pass@host2/db") # 参数会被忽略，因为实例已存在

print(f"conn1 和 conn2 是同一个对象吗? {conn1 is conn2}") # 输出: True
print(f"conn1 的 URL: {conn1.db_url}") # 输出: mysql://user:pass@host1/db
print(f"conn2 的 URL: {conn2.db_url}") # 输出: mysql://user:pass@host1/db
conn1.connect()
conn2.connect()

# 方法三: 使用 __new__ 方法
class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("创建 Logger 单例")
            cls._instance = super(Logger, cls).__new__(cls)
            # 初始化可以在 __new__ 或 __init__ 中进行，但 __init__ 会在每次调用类时执行
            cls._instance.log_file = kwargs.get('log_file', 'app.log')
            cls._instance.logs = []
        return cls._instance

    # 注意: 如果在 __new__ 中完成了初始化，__init__ 仍然会被调用
    # 可以通过检查 _initialized 标志来避免重复初始化
    # def __init__(self, log_file='app.log'):
    #     if not hasattr(self, '_initialized'): # 防止重复初始化
    #         print(f"初始化 Logger (文件: {log_file})")
    #         self.log_file = log_file
    #         self.logs = []
    #         self._initialized = True

    def log(self, message):
        print(f"记录日志到 {self.log_file}: {message}")
        self.logs.append(message)

logger1 = Logger(log_file='debug.log')
logger2 = Logger(log_file='error.log') # log_file 参数在第二次调用时被忽略

print(f"logger1 和 logger2 是同一个对象吗? {logger1 is logger2}") # True
logger1.log("这是一条调试信息")
logger2.log("发生了一个错误")
print(f"Logger1 的日志文件: {logger1.log_file}") # 输出: debug.log
print(f"Logger2 的日志文件: {logger2.log_file}") # 输出: debug.log
print(f"所有日志: {logger1.logs}")

print("\n第5节示例代码结束。")