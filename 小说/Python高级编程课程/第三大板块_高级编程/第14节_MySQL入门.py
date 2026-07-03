# 第14节: MySQL入门
# 内容: MySQL安装配置与卸载、DQL语言

# 注意：运行此代码前，请确保:
# 1. 已安装 MySQL 服务器并正在运行。
# 2. 已创建数据库 'test_db' 和表 'users' (或根据实际情况修改代码)。
#    示例建表语句: 
#    CREATE DATABASE IF NOT EXISTS test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#    USE test_db;
#    CREATE TABLE IF NOT EXISTS users (
#        id INT AUTO_INCREMENT PRIMARY KEY,
#        name VARCHAR(50) NOT NULL,
#        age INT
#    );
#    INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25);
# 3. 已安装 pymysql 库: pip install pymysql

import pymysql
import traceback

print("--- MySQL DQL (Data Query Language) 示例 ---")

# --- 数据库连接配置 --- 
# 请根据您的 MySQL 安装情况修改这些值
DB_CONFIG = {
    'host': '127.0.0.1', # MySQL 服务器地址 (通常是 localhost)
    'port': 3306,         # MySQL 服务器端口 (默认是 3306)
    'user': 'root',       # MySQL 用户名
    'password': 'your_password', # MySQL 密码 (!!!请替换为您的密码!!!)
    'database': 'test_db', # 要连接的数据库名称
    'charset': 'utf8mb4', # 字符集
    'cursorclass': pymysql.cursors.DictCursor # 让查询结果以字典形式返回
}

connection = None
cursor = None

try:
    # --- 1. 建立数据库连接 --- 
    print(f"尝试连接到 MySQL 数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}...")
    connection = pymysql.connect(**DB_CONFIG)
    print("数据库连接成功!")

    # --- 2. 创建游标对象 --- 
    # 游标用于执行 SQL 语句并获取结果
    cursor = connection.cursor()
    print("游标已创建.")

    # --- 3. 执行 DQL 查询 (SELECT) --- 
    sql_query = "SELECT id, name, age FROM users WHERE age > %s"
    min_age = 20
    print(f"执行 SQL 查询: {sql_query} (参数: age > {min_age})")
    
    # 使用参数化查询防止 SQL 注入
    cursor.execute(sql_query, (min_age,))
    print("查询执行完毕.")

    # --- 4. 获取查询结果 --- 
    # fetchone(): 获取下一条结果，如果无结果则返回 None
    # fetchall(): 获取所有结果，返回一个包含所有行的列表（或元组，取决于 cursorclass）
    # fetchmany(size): 获取指定数量的结果
    
    print("\n获取所有查询结果:")
    results = cursor.fetchall()
    
    if results:
        print(f"查询到 {len(results)} 条记录:")
        for row in results:
            # 因为使用了 DictCursor，可以直接通过列名访问
            print(f"  ID: {row['id']}, 姓名: {row['name']}, 年龄: {row['age']}")
    else:
        print("未查询到满足条件的记录。")

    # 示例：获取单条记录
    print("\n尝试获取单条记录 (按 ID 排序):")
    cursor.execute("SELECT id, name FROM users ORDER BY id LIMIT 1")
    single_result = cursor.fetchone()
    if single_result:
        print(f"获取到的第一条记录: ID: {single_result['id']}, 姓名: {single_result['name']}")
    else:
        print("表中没有记录。")

except pymysql.Error as e:
    print(f"\n!!! 数据库操作出错 !!!")
    print(f"错误代码: {e.args[0]}")
    print(f"错误信息: {e.args[1]}")
    print("详细堆栈信息:")
    traceback.print_exc() # 打印详细的错误堆栈
    if e.args[0] == 1045: # Access denied
        print("提示：请检查数据库用户名和密码是否正确。")
    elif e.args[0] == 1049: # Unknown database
        print(f"提示：请确保数据库 '{DB_CONFIG['database']}' 已创建。")
    elif e.args[0] == 2003: # Can't connect to MySQL server
        print(f"提示：请确保 MySQL 服务器正在运行并且地址 '{DB_CONFIG['host']}:{DB_CONFIG['port']}' 可访问。")

except Exception as e:
    print(f"\n!!! 发生未知错误 !!!: {e}")
    traceback.print_exc()

finally:
    # --- 5. 关闭游标和连接 --- 
    # 无论是否发生异常，都应确保关闭资源
    if cursor:
        cursor.close()
        print("\n游标已关闭.")
    if connection:
        connection.close()
        print("数据库连接已关闭.")

print("\nMySQL DQL 示例结束。")

print("\n第14节示例代码结束。")