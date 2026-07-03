# 第15节: SQL语句1
# 内容: 单表查询进阶、DDL操作、DML操作

# 注意：运行此代码前，请确保:
# 1. 已安装 MySQL 服务器并正在运行。
# 2. 已安装 pymysql 库: pip install pymysql
# 3. 数据库连接配置正确 (见下方 DB_CONFIG)。
# 4. 数据库 'test_db' 已存在 (或根据需要修改)。

import pymysql
import traceback

print("--- MySQL DDL, DML, Advanced DQL 示例 ---")

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

    # --- DDL (Data Definition Language) 操作 --- 
    print("\n--- DDL 操作示例 ---")

    # 1. 创建表 (如果不存在)
    try:
        print("尝试创建表 'products'...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            price DECIMAL(10, 2),
            stock INT
        );
        """
        cursor.execute(create_table_sql)
        connection.commit() # DDL 操作通常需要提交
        print("表 'products' 创建成功或已存在.")
    except Exception as e:
        print(f"创建表时出错: {e}")
        connection.rollback() # 出错时回滚

    # 2. 修改表 (添加列)
    try:
        print("尝试向 'products' 表添加 'description' 列...")
        # 检查列是否已存在 (避免重复添加导致错误)
        cursor.execute("SHOW COLUMNS FROM products LIKE 'description'")
        if not cursor.fetchone():
            alter_table_sql = "ALTER TABLE products ADD COLUMN description TEXT AFTER category;"
            cursor.execute(alter_table_sql)
            connection.commit()
            print("'description' 列添加成功.")
        else:
            print("'description' 列已存在.")
    except Exception as e:
        print(f"修改表时出错: {e}")
        connection.rollback()

    # --- DML (Data Manipulation Language) 操作 --- 
    print("\n--- DML 操作示例 ---")

    # 1. 插入数据 (INSERT)
    try:
        print("插入示例数据到 'products' 表...")
        # 使用参数化查询插入多行
        insert_sql = "INSERT INTO products (product_name, category, price, stock, description) VALUES (%s, %s, %s, %s, %s)"
        products_data = [
            ('Laptop Pro', 'Electronics', 1200.50, 50, 'High-performance laptop'),
            ('Coffee Maker', 'Home Appliances', 85.00, 120, 'Brews delicious coffee'),
            ('Python Book', 'Books', 45.99, 200, 'Learn advanced Python')
        ]
        # executemany 用于批量插入
        inserted_rows = cursor.executemany(insert_sql, products_data)
        connection.commit() # DML 操作需要提交才能生效
        print(f"成功插入 {inserted_rows} 条记录.")
    except pymysql.err.IntegrityError as e:
        print(f"插入数据时发生完整性错误 (可能数据已存在): {e}")
        connection.rollback()
    except Exception as e:
        print(f"插入数据时出错: {e}")
        connection.rollback()

    # 2. 更新数据 (UPDATE)
    try:
        print("更新 'Laptop Pro' 的价格...")
        update_sql = "UPDATE products SET price = %s WHERE product_name = %s"
        new_price = 1150.00
        product_to_update = 'Laptop Pro'
        updated_rows = cursor.execute(update_sql, (new_price, product_to_update))
        connection.commit()
        if updated_rows > 0:
            print(f"成功更新了 {updated_rows} 条记录的价格.")
        else:
            print(f"未找到名为 '{product_to_update}' 的产品进行更新.")
    except Exception as e:
        print(f"更新数据时出错: {e}")
        connection.rollback()

    # 3. 删除数据 (DELETE)
    try:
        print("删除价格低于 50 的产品...")
        delete_sql = "DELETE FROM products WHERE price < %s"
        price_threshold = 50.00
        deleted_rows = cursor.execute(delete_sql, (price_threshold,))
        connection.commit()
        if deleted_rows > 0:
            print(f"成功删除了 {deleted_rows} 条记录.")
        else:
            print("没有找到价格低于 50 的产品进行删除.")
    except Exception as e:
        print(f"删除数据时出错: {e}")
        connection.rollback()

    # --- 单表查询进阶 (Advanced DQL) --- 
    print("\n--- 单表查询进阶示例 ---")

    # 1. 条件查询 (WHERE, LIKE)
    print("查询类别为 'Electronics' 的产品:")
    cursor.execute("SELECT product_name, price FROM products WHERE category = %s", ('Electronics',))
    results = cursor.fetchall()
    for row in results: print(f"  - {row['product_name']}: ${row['price']}")

    print("\n查询产品名称包含 'Book' 的产品:")
    cursor.execute("SELECT product_name, category FROM products WHERE product_name LIKE %s", ('%Book%',))
    results = cursor.fetchall()
    for row in results: print(f"  - {row['product_name']} (Category: {row['category']})")

    # 2. 排序 (ORDER BY)
    print("\n按价格降序查询所有产品:")
    cursor.execute("SELECT product_name, price FROM products ORDER BY price DESC")
    results = cursor.fetchall()
    for row in results: print(f"  - {row['product_name']}: ${row['price']}")

    # 3. 限制数量 (LIMIT)
    print("\n查询价格最高的 1 个产品:")
    cursor.execute("SELECT product_name, price FROM products ORDER BY price DESC LIMIT 1")
    result = cursor.fetchone()
    if result: print(f"  - {result['product_name']}: ${result['price']}")

    # 4. 聚合函数 (COUNT, AVG, SUM)
    print("\n查询产品总数:")
    cursor.execute("SELECT COUNT(*) as total_products FROM products")
    result = cursor.fetchone()
    print(f"  - 总产品数: {result['total_products']}")

    print("\n查询平均价格:")
    cursor.execute("SELECT AVG(price) as average_price FROM products")
    result = cursor.fetchone()
    print(f"  - 平均价格: ${result['average_price']:.2f}")

    # 5. 分组 (GROUP BY) 和 分组过滤 (HAVING)
    print("\n按类别统计产品数量:")
    cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category")
    results = cursor.fetchall()
    for row in results: print(f"  - 类别: {row['category']}, 数量: {row['count']}")

    print("\n查询产品数量大于 0 的类别及其平均价格:")
    cursor.execute("""
        SELECT category, AVG(price) as avg_price, COUNT(*) as count
        FROM products 
        GROUP BY category 
        HAVING COUNT(*) > 0
    """)
    results = cursor.fetchall()
    for row in results: print(f"  - 类别: {row['category']}, 平均价格: ${row['avg_price']:.2f}, 数量: {row['count']}")

    # --- 清理操作 (可选) --- 
    # print("\n--- 清理操作 --- ")
    # try:
    #     print("删除 'products' 表...")
    #     cursor.execute("DROP TABLE IF EXISTS products;")
    #     connection.commit()
    #     print("表 'products' 已删除.")
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

print("\nMySQL DDL, DML, Advanced DQL 示例结束。")

print("\n第15节示例代码结束。")