# 第20节: MySQL触发器进阶与函数
# 内容: 触发器的运用、MySQL的UDFs

import mysql.connector
from mysql.connector import errorcode

# 数据库连接配置 (请根据实际情况修改)
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'database': 'test_db', # 确保这个数据库存在
    'raise_on_warnings': True
}

def create_connection():
    """创建数据库连接"""
    try:
        # 尝试连接时不指定数据库，连接成功后再选择
        conn_init = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            raise_on_warnings=db_config['raise_on_warnings']
        )
        cursor = conn_init.cursor()
        # 检查数据库是否存在，如果不存在则创建
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn_init.close()

        # 正式连接到指定数据库
        conn = mysql.connector.connect(**db_config)
        print("数据库连接成功")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("用户名或密码错误")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"数据库 '{db_config['database']}' 不存在或无法访问，请检查配置或权限")
        else:
            print(f"连接错误: {err}")
        return None

def execute_query(conn, query, data=None, multi=False):
    """执行SQL查询"""
    cursor = conn.cursor()
    try:
        if multi:
            # 对于可能包含多个语句的 CREATE TRIGGER/FUNCTION，使用 multi=True
            # 注意：这要求连接时允许执行多语句，或者需要特殊处理
            # mysql-connector-python 不直接支持 DELIMITER，通常需要分割语句
            # 这里简化处理，假设单条语句或服务器配置允许
            results = cursor.execute(query, multi=True)
            # multi=True 时返回迭代器，需要遍历处理
            for result in results:
                print(f"  语句结果: {result.statement}")
            print(f"执行多语句成功: {query[:50]}...")
        elif data:
            cursor.execute(query, data)
            print(f"执行成功 (带参数): {query[:50]}...")
        else:
            cursor.execute(query)
            print(f"执行成功: {query[:50]}...")
        conn.commit()
    except mysql.connector.Error as err:
        print(f"执行失败: {err}")
        print(f"失败的查询: {query}")
        conn.rollback()
    finally:
        cursor.close()

def execute_script(conn, sql_script):
    """执行可能包含多个语句的SQL脚本 (尝试分割)"""
    cursor = conn.cursor()
    try:
        # 简单的按 ';' 分割，可能对复杂脚本无效
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for stmt in statements:
            print(f"执行语句: {stmt[:60]}...")
            cursor.execute(stmt)
        conn.commit()
        print("脚本执行成功")
    except mysql.connector.Error as err:
        print(f"脚本执行失败: {err}")
        conn.rollback()
    finally:
        cursor.close()

def create_sample_tables(conn):
    """创建示例表"""
    print("\n--- 创建示例表 ---")
    # 创建产品表
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        stock INT DEFAULT 0
    ) ENGINE=InnoDB;
    """
    execute_query(conn, create_products_table)

    # 创建订单表
    create_orders_table = """
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT,
        quantity INT NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """
    execute_query(conn, create_orders_table)

    # 创建日志表
    create_log_table = """
    CREATE TABLE IF NOT EXISTS product_log (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT,
        action VARCHAR(50),
        old_price DECIMAL(10, 2),
        new_price DECIMAL(10, 2),
        change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    execute_query(conn, create_log_table)

def drop_trigger_if_exists(conn, trigger_name):
    """如果触发器存在则删除"""
    query = f"DROP TRIGGER IF EXISTS {trigger_name};"
    execute_query(conn, query)

def create_update_trigger(conn):
    """创建更新产品价格时记录日志的触发器"""
    print("\n--- 创建更新触发器 --- ")
    trigger_name = "log_product_price_update"
    drop_trigger_if_exists(conn, trigger_name)

    # 使用 DELIMITER 语法在 Python 中通常不可靠，最好是单条语句
    # 或者使用存储过程来创建触发器
    create_trigger_sql = f"""
    CREATE TRIGGER {trigger_name}
    AFTER UPDATE ON products
    FOR EACH ROW
    BEGIN
        IF OLD.price <> NEW.price THEN
            INSERT INTO product_log (product_id, action, old_price, new_price)
            VALUES (OLD.product_id, 'UPDATE_PRICE', OLD.price, NEW.price);
        END IF;
    END
    """ # 注意：移除了末尾的 ; 以便 execute_query 处理
    # 尝试直接执行，如果失败，说明需要特殊处理（如通过存储过程创建）
    execute_query(conn, create_trigger_sql)

def create_insert_trigger(conn):
    """创建插入订单时更新库存的触发器"""
    print("\n--- 创建插入触发器 --- ")
    trigger_name = "update_stock_on_order"
    drop_trigger_if_exists(conn, trigger_name)

    create_trigger_sql = f"""
    CREATE TRIGGER {trigger_name}
    AFTER INSERT ON orders
    FOR EACH ROW
    BEGIN
        UPDATE products
        SET stock = stock - NEW.quantity
        WHERE product_id = NEW.product_id;
    END
    """
    execute_query(conn, create_trigger_sql)

def demonstrate_triggers(conn):
    """演示触发器的效果"""
    print("\n--- 演示触发器 --- ")
    cursor = conn.cursor(dictionary=True) # 使用字典游标方便访问列

    # 0. 清空旧数据（可选，用于重复运行脚本）
    print("\n0. 清理旧数据 (可选)")
    execute_query(conn, "DELETE FROM product_log")
    execute_query(conn, "DELETE FROM orders")
    execute_query(conn, "DELETE FROM products")

    # 1. 插入一个产品
    print("\n1. 插入产品:")
    insert_product_sql = "INSERT INTO products (product_name, price, stock) VALUES (%s, %s, %s)"
    product_data = ('Laptop X1', 1200.00, 50)
    execute_query(conn, insert_product_sql, product_data)

    # 获取刚插入的产品ID
    cursor.execute("SELECT product_id FROM products WHERE product_name = %s", (product_data[0],))
    result = cursor.fetchone()
    if not result:
        print("错误：未能获取新插入产品的ID")
        return
    product_id = result['product_id']
    print(f"产品 '{product_data[0]}' 插入成功, ID: {product_id}")

    # 2. 更新产品价格 (触发 log_product_price_update)
    print("\n2. 更新产品价格:")
    update_price_sql = "UPDATE products SET price = %s WHERE product_id = %s"
    new_price_data = (1150.00, product_id)
    execute_query(conn, update_price_sql, new_price_data)
    print(f"产品 ID {product_id} 价格更新为 {new_price_data[0]}")

    # 查看日志表
    print("\n查看价格更新日志:")
    cursor.execute("SELECT * FROM product_log WHERE product_id = %s", (product_id,))
    log_entry = cursor.fetchone()
    if log_entry:
        print(f"日志记录: {log_entry}")
        assert log_entry['old_price'] == 1200.00
        assert log_entry['new_price'] == 1150.00
    else:
        print("错误：未找到相关日志记录，触发器可能未成功创建或执行")

    # 3. 插入一个订单 (触发 update_stock_on_order)
    print("\n3. 插入订单:")
    insert_order_sql = "INSERT INTO orders (product_id, quantity) VALUES (%s, %s)"
    order_data = (product_id, 2)
    execute_query(conn, insert_order_sql, order_data)
    print(f"为产品 ID {product_id} 创建了数量为 {order_data[1]} 的订单")

    # 查看产品库存
    print("\n查看更新后的库存:")
    cursor.execute("SELECT stock FROM products WHERE product_id = %s", (product_id,))
    stock_result = cursor.fetchone()
    if stock_result:
        stock = stock_result['stock']
        print(f"产品 ID {product_id} 当前库存: {stock}")
        expected_stock = product_data[2] - order_data[1]
        assert stock == expected_stock # 预期: 50 - 2 = 48
    else:
        print(f"错误：未能查询到产品 ID {product_id} 的库存")

    cursor.close()

def drop_function_if_exists(conn, func_name):
    """如果函数存在则删除"""
    query = f"DROP FUNCTION IF EXISTS {func_name};"
    execute_query(conn, query)

def create_udf_calculate_discount(conn):
    """创建计算折扣价的UDF"""
    print("\n--- 创建用户定义函数 (UDF) --- ")
    func_name = "calculate_discounted_price"
    drop_function_if_exists(conn, func_name)

    create_func_sql = f"""
    CREATE FUNCTION {func_name}(original_price DECIMAL(10, 2), discount_rate DECIMAL(3, 2))
    RETURNS DECIMAL(10, 2)
    DETERMINISTIC
    BEGIN
        DECLARE discounted_price DECIMAL(10, 2);
        IF discount_rate < 0 OR discount_rate > 1 THEN
            -- 无效折扣率，返回原价
            SET discounted_price = original_price;
        ELSE
            SET discounted_price = original_price * (1.0 - discount_rate);
        END IF;
        RETURN discounted_price;
    END
    """
    execute_query(conn, create_func_sql)

def demonstrate_udf(conn):
    """演示UDF的使用"""
    print("\n--- 演示用户定义函数 (UDF) --- ")
    cursor = conn.cursor(dictionary=True)

    # 确保有产品数据用于测试
    cursor.execute("SELECT product_id, product_name, price FROM products LIMIT 1")
    product = cursor.fetchone()
    if not product:
        print("没有产品数据可用于演示 UDF，请先运行触发器演示部分")
        cursor.close()
        return

    product_id = product['product_id']
    product_name = product['product_name']
    original_price = product['price']
    discount = 0.10 # 10% 折扣

    # 使用 UDF 查询产品折扣价
    print(f"\n使用 UDF 计算产品 '{product_name}' (ID: {product_id}) 的折扣价 (折扣率 {discount}):")
    query = f"""
    SELECT
        calculate_discounted_price(%s, %s) AS discounted_price;
    """
    try:
        cursor.execute(query, (original_price, discount))
        result = cursor.fetchone()
        if result:
            calculated_discounted_price = result['discounted_price']
            print(f"原价: {original_price}, UDF计算折扣价: {calculated_discounted_price}")
            expected_price = original_price * (1.0 - discount)
            # 比较 DECIMAL 类型时注意精度问题
            assert abs(calculated_discounted_price - expected_price) < 0.001
        else:
            print("未能使用 UDF 计算价格")
    except mysql.connector.Error as err:
        print(f"查询失败: {err}")
    finally:
        cursor.close()

def cleanup(conn):
    """清理创建的表、触发器和函数"""
    print("\n--- 清理环境 --- ")
    cursor = conn.cursor()
    try:
        print("删除触发器...")
        drop_trigger_if_exists(conn, "log_product_price_update")
        drop_trigger_if_exists(conn, "update_stock_on_order")

        print("删除函数...")
        drop_function_if_exists(conn, "calculate_discounted_price")

        print("删除表 (按依赖顺序)...")
        execute_query(conn, "DROP TABLE IF EXISTS product_log;")
        execute_query(conn, "DROP TABLE IF EXISTS orders;")
        execute_query(conn, "DROP TABLE IF EXISTS products;")

        print("清理完成")
    except mysql.connector.Error as err:
        print(f"清理失败: {err}")
        # 不回滚，尽量删除
    finally:
        cursor.close()


if __name__ == "__main__":
    print("开始执行 MySQL 触发器与函数演示脚本")
    print("请确保 MySQL 服务正在运行，并已正确配置 db_config 中的用户名、密码和主机")
    print(f"将尝试连接到数据库: {db_config.get('database', '未指定')}")

    connection = create_connection()

    if connection and connection.is_connected():
        try:
            # 准备环境
            # 注意：首次运行时清理可能无操作，但有助于重复执行
            cleanup(connection)
            create_sample_tables(connection)

            # 触发器演示
            create_update_trigger(connection)
            create_insert_trigger(connection)
            demonstrate_triggers(connection)

            # UDF 演示
            create_udf_calculate_discount(connection)
            demonstrate_udf(connection)

            print("\n演示完成！")

        except Exception as e:
            print(f"\n发生意外错误: {e}")
        finally:
            # 再次清理本次运行创建的对象
            print("\n执行最终清理...")
            cleanup(connection)
            print("\n关闭数据库连接")
            connection.close()
    else:
        print("\n未能连接到数据库，脚本终止。请检查配置和 MySQL 服务状态。")