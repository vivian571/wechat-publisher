# 第17节: MySQL的多表查询与视图
# 内容: 多表关联查询、join连接、视图

# 注意：运行此代码前，请确保:
# 1. 已安装 MySQL 服务器并正在运行。
# 2. 已安装 pymysql 库: pip install pymysql
# 3. 数据库连接配置正确 (见下方 DB_CONFIG)。
# 4. 数据库 'test_db' 已存在，并且包含前几节创建的 'customers' 和 'orders' 表。
#    如果表不存在，请先运行第16节的代码创建并填充数据。

import pymysql
import traceback

print("--- MySQL 多表查询复习 与 视图 (View) 示例 ---")

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

    # --- 多表关联查询 (JOIN 复习) --- 
    print("\n--- 多表关联查询 (JOIN 复习) ---")

    # 1. INNER JOIN (查找同时在两表中有匹配的记录)
    print("查询下过单的客户及其订单信息 (INNER JOIN):")
    cursor.execute("""
        SELECT c.customer_name, o.order_id, o.total_amount
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        WHERE c.customer_name = %s;
    """, ('张三',))
    results = cursor.fetchall()
    for row in results: print(f"  - 客户: {row['customer_name']}, 订单ID: {row['order_id']}, 金额: {row['total_amount']}")

    # 2. LEFT JOIN (以左表为主，显示所有客户，无论是否有订单)
    print("\n查询所有客户及其首个订单日期 (LEFT JOIN):")
    cursor.execute("""
        SELECT c.customer_name, MIN(o.order_date) as first_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name
        ORDER BY c.customer_name;
    """)
    results = cursor.fetchall()
    for row in results:
        date_str = row['first_order_date'].strftime('%Y-%m-%d') if row['first_order_date'] else '无订单'
        print(f"  - 客户: {row['customer_name']}, 首次下单日期: {date_str}")

    # 3. RIGHT JOIN (以右表为主，显示所有订单及其客户信息，MySQL支持)
    #    (假设有一个订单的 customer_id 在 customers 表中不存在，虽然我们设置了外键)
    print("\n查询所有订单及其客户信息 (RIGHT JOIN):")
    # 为了演示，我们先手动插入一个 customer_id 不存在的订单 (临时取消外键检查)
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, %s, %s)", (99, '2024-03-15 12:00:00', 10.00))
        connection.commit()
        print("  (临时插入了一个 customer_id=99 的订单用于演示)")
        cursor.execute("""
            SELECT c.customer_name, o.order_id, o.customer_id as order_customer_id
            FROM customers c
            RIGHT JOIN orders o ON c.customer_id = o.customer_id
            ORDER BY o.order_id;
        """)
        results = cursor.fetchall()
        for row in results:
            cust_name = row['customer_name'] if row['customer_name'] else '未知客户'
            print(f"  - 订单ID: {row['order_id']}, 客户: {cust_name} (订单关联客户ID: {row['order_customer_id']})")
        # 清理演示数据
        cursor.execute("DELETE FROM orders WHERE customer_id = 99")
        connection.commit()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        print("  (已清理临时订单数据)")
    except Exception as e:
        print(f"  执行 RIGHT JOIN 演示时出错: {e}")
        connection.rollback()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    # --- 视图 (View) --- 
    print("\n--- 视图 (View) 示例 ---")

    # 1. 创建视图
    view_name = 'customer_order_summary'
    print(f"尝试创建视图 '{view_name}'...")
    try:
        # 如果视图已存在，先删除 (或者使用 CREATE OR REPLACE VIEW)
        cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        create_view_sql = f"""
        CREATE VIEW {view_name} AS
        SELECT 
            c.customer_name,
            c.email,
            COUNT(o.order_id) AS order_count,
            SUM(o.total_amount) AS total_spent,
            MAX(o.order_date) AS last_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name, c.email;
        """
        cursor.execute(create_view_sql)
        connection.commit() # DDL 操作需要提交
        print(f"视图 '{view_name}' 创建成功.")
    except Exception as e:
        print(f"创建视图时出错: {e}")
        connection.rollback()

    # 2. 查询视图
    print(f"\n查询视图 '{view_name}':")
    try:
        cursor.execute(f"SELECT * FROM {view_name} WHERE order_count > 0 ORDER BY total_spent DESC;")
        results = cursor.fetchall()
        if results:
            for row in results:
                spent = row['total_spent'] if row['total_spent'] else 0.00
                last_date = row['last_order_date'].strftime('%Y-%m-%d %H:%M') if row['last_order_date'] else 'N/A'
                print(f"  - 客户: {row['customer_name']} ({row['email']}), 订单数: {row['order_count']}, 总消费: ${spent:.2f}, 最后订单: {last_date}")
        else:
            print("  视图中没有数据或查询无结果.")
    except Exception as e:
        print(f"查询视图时出错: {e}")

    # 3. 修改视图 (使用 CREATE OR REPLACE VIEW)
    print(f"\n尝试修改视图 '{view_name}' (添加 join_date)..." )
    try:
        alter_view_sql = f"""
        CREATE OR REPLACE VIEW {view_name} AS
        SELECT 
            c.customer_name,
            c.email,
            c.join_date,  -- 新增列
            COUNT(o.order_id) AS order_count,
            SUM(o.total_amount) AS total_spent,
            MAX(o.order_date) AS last_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name, c.email, c.join_date;
        """
        cursor.execute(alter_view_sql)
        connection.commit()
        print(f"视图 '{view_name}' 修改成功.")
        # 再次查询验证
        cursor.execute(f"SELECT customer_name, join_date FROM {view_name} LIMIT 1;")
        result = cursor.fetchone()
        if result:
            print(f"  验证修改后视图: 客户: {result['customer_name']}, 加入日期: {result['join_date']}")

    except Exception as e:
        print(f"修改视图时出错: {e}")
        connection.rollback()

    # 4. 删除视图
    print(f"\n尝试删除视图 '{view_name}'...")
    try:
        cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        connection.commit()
        print(f"视图 '{view_name}' 删除成功.")
    except Exception as e:
        print(f"删除视图时出错: {e}")
        connection.rollback()

except pymysql.Error as e:
    print(f"\n!!! 数据库操作出错 !!!")
    print(f"错误代码: {e.args[0]}")
    print(f"错误信息: {e.args[1]}")
    traceback.print_exc()
    if e.args[0] == 1045: print("提示：请检查数据库用户名和密码。")
    elif e.args[0] == 1049: print(f"提示：请确保数据库 '{DB_CONFIG['database']}' 已创建。")
    elif e.args[0] == 2003: print(f"提示：请确保 MySQL 服务器正在运行。")
    elif e.args[0] == 1146: print("提示：查询的表或视图不存在，请确保已运行之前的脚本创建了必要的表。")
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

print("\nMySQL 多表查询与视图 示例结束。")

print("\n第17节示例代码结束。")