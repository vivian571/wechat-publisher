# 第18节: MySQL视图进阶与存储过程
# 内容: 复杂视图、存储过程的创建调用、存储过程的变量与赋值

# 注意：运行此代码前，请确保:
# 1. 已安装 MySQL 服务器并正在运行。
# 2. 已安装 pymysql 库: pip install pymysql
# 3. 数据库连接配置正确 (见下方 DB_CONFIG)。
# 4. 数据库 'test_db' 已存在，并且包含 'customers', 'orders', 'products', 'order_items' 表。
#    如果表不存在，请先运行之前的脚本创建并填充数据。
#    (可能需要创建 products 和 order_items 表)
#    示例建表 (如果需要):
#    CREATE TABLE IF NOT EXISTS products (
#        product_id INT AUTO_INCREMENT PRIMARY KEY,
#        product_name VARCHAR(100) NOT NULL,
#        price DECIMAL(10, 2) NOT NULL
#    );
#    INSERT INTO products (product_name, price) VALUES ('Laptop', 1200.00), ('Mouse', 25.00), ('Keyboard', 75.00);
#    CREATE TABLE IF NOT EXISTS order_items (
#        item_id INT AUTO_INCREMENT PRIMARY KEY,
#        order_id INT,
#        product_id INT,
#        quantity INT NOT NULL,
#        FOREIGN KEY (order_id) REFERENCES orders(order_id),
#        FOREIGN KEY (product_id) REFERENCES products(product_id)
#    );

import pymysql
import traceback

print("--- MySQL 复杂视图 与 存储过程 (含变量) 示例 ---")

# --- 数据库连接配置 --- 
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'your_password', # !!!请替换为您的密码!!!
    'database': 'test_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

connection = None
cursor = None

try:
    # --- 建立连接和游标 ---
    print(f"尝试连接到 MySQL 数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}...")
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    print("数据库连接成功，游标已创建.")

    # --- 复杂视图 (Complex View) ---
    print("\n--- 复杂视图示例 ---")

    # 1. 创建一个复杂视图 (连接三张表: customers, orders, order_items, products)
    complex_view_name = 'customer_order_details'
    print(f"尝试创建或替换复杂视图 '{complex_view_name}'...")
    try:
        # 如果视图已存在，先删除
        cursor.execute(f"DROP VIEW IF EXISTS {complex_view_name};")
        create_complex_view_sql = f"""
        CREATE VIEW {complex_view_name} AS
        SELECT
            c.customer_name,
            o.order_id,
            o.order_date,
            p.product_name,
            oi.quantity,
            p.price AS unit_price,
            (oi.quantity * p.price) AS item_total -- 计算项总价
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id;
        """
        cursor.execute(create_complex_view_sql)
        connection.commit()
        print(f"复杂视图 '{complex_view_name}' 创建/替换成功.")
    except Exception as e:
        print(f"创建复杂视图时出错: {e}")
        connection.rollback()

    # 2. 查询复杂视图
    print(f"\n查询复杂视图 '{complex_view_name}' (查询张三的订单详情):")
    try:
        cursor.execute(f"SELECT * FROM {complex_view_name} WHERE customer_name = %s ORDER BY order_date DESC, product_name;", ('张三',))
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"  - 客户: {row['customer_name']}, 订单ID: {row['order_id']}, 日期: {row['order_date'].strftime('%Y-%m-%d')}, "
                      f"产品: {row['product_name']}, 数量: {row['quantity']}, 单价: {row['unit_price']:.2f}, 项总价: {row['item_total']:.2f}")
        else:
            print("  未查询到张三的订单详情。请确保相关表中有数据且视图创建成功。")
    except Exception as e:
        print(f"查询复杂视图时出错: {e}")

    # --- 存储过程 (Stored Procedure) 基础 ---
    print("\n--- 存储过程 (创建、调用、变量、赋值) 示例 ---")

    # 1. 创建一个简单的存储过程 (无参数)
    sp_simple_name = 'sp_get_customer_count'
    print(f"\n尝试创建存储过程 '{sp_simple_name}'...")
    try:
        cursor.execute(f"DROP PROCEDURE IF EXISTS {sp_simple_name};")
        # 注意：在 Python 中执行多语句的存储过程定义，可能需要特殊处理或在 MySQL 客户端执行
        # 这里用简单示例演示基本调用
        # DELIMITER //  -- 在 Python 客户端通常不需要设置 DELIMITER
        create_sp_simple_sql = f"""
        CREATE PROCEDURE {sp_simple_name}()
        BEGIN
            SELECT COUNT(*) AS total_customers FROM customers;
        END;
        """ # DELIMITER ; -- 恢复默认
        cursor.execute(create_sp_simple_sql)
        connection.commit()
        print(f"存储过程 '{sp_simple_name}' 创建成功.")
    except Exception as e:
        print(f"创建简单存储过程时出错: {e}")
        connection.rollback()

    # 2. 调用简单存储过程
    print(f"\n调用存储过程 '{sp_simple_name}':")
    try:
        cursor.callproc(sp_simple_name) # 使用 callproc 调用
        result = cursor.fetchone()
        if result:
            print(f"  客户总数: {result['total_customers']}")
        # 对于返回结果集的存储过程，需要获取结果
        # 如果存储过程修改数据，则不需要 fetch
        # 需要读取存储过程返回的所有结果集，即使只有一个
        # 否则可能出现 Commands out of sync 错误
        while cursor.nextset():
            pass
    except Exception as e:
        print(f"调用简单存储过程时出错: {e}")

    # 3. 创建带变量和赋值的存储过程 (IN 输入参数, OUT 输出参数)
    sp_vars_name = 'sp_get_customer_orders_info'
    print(f"\n尝试创建带变量的存储过程 '{sp_vars_name}'...")
    try:
        cursor.execute(f"DROP PROCEDURE IF EXISTS {sp_vars_name};")
        # DELIMITER //
        create_sp_vars_sql = f"""
        CREATE PROCEDURE {sp_vars_name}(
            IN customerId INT,         -- 输入参数：客户ID
            OUT totalOrders INT,       -- 输出参数：订单总数
            OUT totalAmount DECIMAL(10, 2) -- 输出参数：总消费金额
        )
        BEGIN
            -- 声明局部变量
            DECLARE order_count INT DEFAULT 0;
            DECLARE spent_amount DECIMAL(10, 2) DEFAULT 0.00;

            -- 查询并赋值给变量
            SELECT COUNT(order_id), SUM(total_amount)
            INTO order_count, spent_amount -- 将查询结果赋值给变量
            FROM orders
            WHERE customer_id = customerId;

            -- 将局部变量的值赋给输出参数
            SET totalOrders = order_count;
            SET totalAmount = spent_amount;
        END;
        """ # DELIMITER ;
        cursor.execute(create_sp_vars_sql)
        connection.commit()
        print(f"带变量的存储过程 '{sp_vars_name}' 创建成功.")
    except Exception as e:
        print(f"创建带变量存储过程时出错: {e}")
        connection.rollback()

    # 4. 调用带变量的存储过程
    print(f"\n调用存储过程 '{sp_vars_name}' (查询客户ID=1的信息):")
    try:
        customer_id_to_check = 1
        # 调用存储过程，传入输入参数，并初始化输出参数变量 (在会话中)
        # pymysql 的 callproc 会自动处理 OUT 参数，但获取方式略有不同
        # result_args = cursor.callproc(sp_vars_name, (customer_id_to_check, 0, 0.0)) # 初始值会被忽略

        # 更标准的 SQL 调用方式 (推荐)
        cursor.execute(f"CALL {sp_vars_name}(%s, @out_total_orders, @out_total_amount);", (customer_id_to_check,))
        # 获取 OUT 参数的值
        cursor.execute("SELECT @out_total_orders, @out_total_amount;")
        out_params = cursor.fetchone()

        if out_params:
            # 注意：键名包含@符号
            total_orders = out_params['@out_total_orders']
            total_amount = out_params['@out_total_amount']
            print(f"  客户ID {customer_id_to_check} 的信息:")
            print(f"    订单总数: {total_orders}")
            print(f"    总消费金额: {total_amount if total_amount else '0.00'}") # 处理 NULL 情况
        else:
             print(f"  未能获取客户ID {customer_id_to_check} 的输出参数。")
        # 确保读取所有结果集
        while cursor.nextset():
            pass
    except Exception as e:
        print(f"调用带变量存储过程时出错: {e}")

    # --- 清理 (可选) ---
    # print("\n--- 清理创建的视图和存储过程 ---")
    # try:
    #     cursor.execute(f"DROP VIEW IF EXISTS {complex_view_name};")
    #     cursor.execute(f"DROP PROCEDURE IF EXISTS {sp_simple_name};")
    #     cursor.execute(f"DROP PROCEDURE IF EXISTS {sp_vars_name};")
    #     connection.commit()
    #     print("视图和存储过程已删除。")
    # except Exception as e:
    #     print(f"清理时出错: {e}")
    #     connection.rollback()


except pymysql.Error as e:
    print(f"\n!!! 数据库操作出错 !!!")
    print(f"错误代码: {e.args[0]}")
    print(f"错误信息: {e.args[1]}")
    traceback.print_exc()
    if e.args[0] == 1045: print("提示：请检查数据库用户名和密码。")
    elif e.args[0] == 1049: print(f"提示：请确保数据库 '{DB_CONFIG['database']}' 已创建。")
    elif e.args[0] == 2003: print(f"提示：请确保 MySQL 服务器正在运行。")
    elif e.args[0] == 1146: print("提示：查询的表或视图不存在，请确保已运行之前的脚本创建了必要的表。")
    if connection: connection.rollback()

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

print("\n第18节示例代码结束。")