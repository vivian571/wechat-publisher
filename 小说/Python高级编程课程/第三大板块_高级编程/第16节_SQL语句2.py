# 第16节: SQL语句2
# 内容: 数据库操作案例、多表关联、DML操作进阶

# 注意：运行此代码前，请确保:
# 1. 已安装 MySQL 服务器并正在运行。
# 2. 已安装 pymysql 库: pip install pymysql
# 3. 数据库连接配置正确 (见下方 DB_CONFIG)。
# 4. 数据库 'test_db' 已存在，并且可能需要前几节创建的 'users' 和 'products' 表（如果案例涉及）。

import pymysql
import traceback
import datetime

print("--- MySQL 多表关联, DML进阶, 案例 示例 ---")

# --- 数据库连接配置 --- 
# 请根据您的 MySQL 安装情况修改这些值
DB_CONFIG = {
    'host': '127.0.0.1', # MySQL 服务器地址
    'port': 3306,         # MySQL 服务器端口
    'user': 'root',       # MySQL 用户名
    'password': 'your_password', # !!!请替换为您的密码!!!
    'database': 'test_db', # 数据库名称
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # 结果以字典形式返回
}

connection = None
cursor = None

try:
    # --- 建立连接和游标 --- 
    print(f"尝试连接到 MySQL 数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}...")
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    print("数据库连接成功，游标已创建.")

    # --- 准备示例数据 (创建 customers 和 orders 表) ---
    print("\n--- 准备多表示例数据 ---")
    try:
        print("创建 'customers' 表 (如果不存在)...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            join_date DATE
        );
        """)
        print("创建 'orders' 表 (如果不存在)...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            order_date DATETIME,
            total_amount DECIMAL(10, 2),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
        );
        """)
        connection.commit()
        print("'customers' 和 'orders' 表创建成功或已存在.")

        # 清理旧数据（可选，确保每次运行结果一致）
        # print("清理旧的订单和客户数据...")
        # cursor.execute("DELETE FROM orders")
        # cursor.execute("DELETE FROM customers")
        # connection.commit()

        # 插入客户数据 (使用 DML 进阶: INSERT ... ON DUPLICATE KEY UPDATE)
        print("插入或更新客户数据...")
        insert_customer_sql = """
        INSERT INTO customers (customer_id, customer_name, email, join_date)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE customer_name = VALUES(customer_name), join_date = VALUES(join_date);
        """
        customers_data = [
            (1, '张三', 'zhangsan@example.com', '2023-01-15'),
            (2, '李四', 'lisi@example.com', '2023-02-20'),
            (3, '王五', 'wangwu@example.com', '2023-01-15') # 重复ID，会更新
        ]
        # 注意：ON DUPLICATE KEY UPDATE 依赖于 PRIMARY KEY 或 UNIQUE 索引
        # 这里我们用 customer_id 作为主键来演示，如果 email 是 UNIQUE 也可以触发
        inserted_customers = cursor.executemany(insert_customer_sql, customers_data)
        connection.commit()
        print(f"处理了 {inserted_customers} 行客户数据 (插入或更新).")

        # 插入订单数据
        print("插入订单数据...")
        insert_order_sql = "INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, %s, %s)"
        orders_data = [
            (1, datetime.datetime(2024, 3, 10, 10, 30, 0), 150.75),
            (2, datetime.datetime(2024, 3, 11, 14, 0, 0), 88.50),
            (1, datetime.datetime(2024, 3, 12, 9, 15, 0), 210.00),
            (3, datetime.datetime(2024, 3, 10, 11, 0, 0), 55.20)
        ]
        inserted_orders = cursor.executemany(insert_order_sql, orders_data)
        connection.commit()
        print(f"成功插入 {inserted_orders} 条订单记录.")

    except Exception as e:
        print(f"准备数据时出错: {e}")
        connection.rollback()

    # --- 多表关联查询 (JOIN) --- 
    print("\n--- 多表关联查询示例 --- ")

    # 1. 内连接 (INNER JOIN): 获取同时存在于 customers 和 orders 表中的匹配记录
    print("查询所有客户及其订单信息 (INNER JOIN):")
    inner_join_sql = """
    SELECT c.customer_name, c.email, o.order_id, o.order_date, o.total_amount
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    ORDER BY c.customer_name, o.order_date;
    """
    cursor.execute(inner_join_sql)
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"  - 客户: {row['customer_name']} ({row['email']}), 订单ID: {row['order_id']}, 日期: {row['order_date']}, 金额: {row['total_amount']}")
    else:
        print("  未查询到匹配的客户订单信息.")

    # 2. 左连接 (LEFT JOIN): 获取左表(customers)的所有记录，以及右表(orders)中的匹配记录
    print("\n查询所有客户信息，以及他们的订单信息 (LEFT JOIN):")
    left_join_sql = """
    SELECT c.customer_name, c.email, o.order_id, o.order_date, o.total_amount
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    ORDER BY c.customer_name;
    """
    cursor.execute(left_join_sql)
    results = cursor.fetchall()
    if results:
        for row in results:
            order_info = f"订单ID: {row['order_id']}, 日期: {row['order_date']}, 金额: {row['total_amount']}" if row['order_id'] else "无订单"
            print(f"  - 客户: {row['customer_name']} ({row['email']}), {order_info}")
    else:
        print("  未查询到客户信息.")

    # 3. 查询没有下过订单的客户 (使用 LEFT JOIN + WHERE IS NULL)
    print("\n查询没有下过订单的客户:")
    no_order_sql = """
    SELECT c.customer_name, c.email
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_id IS NULL;
    """
    cursor.execute(no_order_sql)
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"  - 客户: {row['customer_name']} ({row['email']})")
    else:
        print("  所有客户都有订单记录.")

    # --- 数据库操作案例：统计每个客户的订单总额 --- 
    print("\n--- 案例：统计每个客户的订单总额 --- ")
    case_sql = """
    SELECT c.customer_name, COUNT(o.order_id) as order_count, SUM(o.total_amount) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name # 分组依据客户ID和名称
    ORDER BY total_spent DESC;
    """
    cursor.execute(case_sql)
    results = cursor.fetchall()
    if results:
        print("客户订单统计:")
        for row in results:
            total_spent = row['total_spent'] if row['total_spent'] is not None else 0.00
            print(f"  - 客户: {row['customer_name']}, 订单数: {row['order_count']}, 总消费: ${total_spent:.2f}")
    else:
        print("  无法生成客户订单统计.")

    # --- 清理操作 (可选) --- 
    # print("\n--- 清理示例表 --- ")
    # try:
    #     print("删除 'orders' 和 'customers' 表...")
    #     cursor.execute("DROP TABLE IF EXISTS orders;")
    #     cursor.execute("DROP TABLE IF EXISTS customers;")
    #     connection.commit()
    #     print("示例表已删除.")
    # except Exception as e:
    #     print(f"删除表时出错: {e}")
    #     connection.rollback()

except pymysql.Error as e:
    print(f"\n!!! 数据库操作出错 !!!")
    print(f"错误代码: {e.args[0]}")
    print(f"错误信息: {e.args[1]}")
    traceback.print_exc()
    if e.args[0] == 1045: print("提示：请检查数据库用户名和密码。")
    elif e.args[0] == 1049: print(f"提示：请确保数据库 '{DB_CONFIG['database']}' 已创建。")
    elif e.args[0] == 2003: print(f"提示：请确保 MySQL 服务器正在运行。")
    if connection: connection.rollback() # 发生错误时回滚

except Exception as e:
    print(f"\n!!! 发生未知错误 !!!: {e}")
    traceback.print_exc()
    if connection: connection.rollback()

finally:
    # --- 关闭游标和连接 --- 
    if cursor:
        cursor.close()
        print("\n游标已关闭.")
    if connection:
        connection.close()
        print("数据库连接已关闭.")

print("\nMySQL 多表关联, DML进阶, 案例 示例结束。")

print("\n第16节示例代码结束。")