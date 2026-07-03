# 第22节: pymysql
# 内容: pymysql的运用、CRUD数据操作

import pymysql
from pymysql.cursors import DictCursor

# 数据库连接配置 (请根据实际情况修改)
# 注意: pymysql 的参数名与 mysql.connector 不同
db_config = {
    'host': '127.0.0.1',
    'port': 3306, # pymysql 默认端口也是 3306
    'user': 'your_username',
    'password': 'your_password',
    'database': 'test_db', # 确保这个数据库存在
    'charset': 'utf8mb4',
    'cursorclass': DictCursor # 使用字典游标，方便按列名访问
}

def create_connection():
    """使用 pymysql 创建数据库连接"""
    try:
        # 尝试连接时不指定数据库，连接成功后再选择
        conn_init = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            charset=db_config['charset']
        )
        with conn_init.cursor() as cursor:
            # 检查数据库是否存在，如果不存在则创建
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_config['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn_init.close()

        # 正式连接到指定数据库
        conn = pymysql.connect(**db_config)
        print("数据库连接成功 (使用 pymysql)")
        return conn
    except pymysql.Error as err:
        print(f"连接错误 (pymysql): {err}")
        # 可以根据 err.args[0] 判断具体错误类型，例如 1045 是访问拒绝
        if err.args[0] == 1045:
            print("用户名或密码错误")
        elif err.args[0] == 1049:
            print(f"数据库 '{db_config['database']}' 不存在")
        return None

def create_sample_table(conn):
    """创建用于 CRUD 演示的用户表"""
    print("\n--- 创建示例用户表 (users) ---")
    with conn.cursor() as cursor:
        drop_table_sql = "DROP TABLE IF EXISTS users;"
        cursor.execute(drop_table_sql)
        print("旧的 users 表 (如果存在) 已删除")

        create_table_sql = """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            age INT
        ) ENGINE=InnoDB CHARSET=utf8mb4;
        """
        cursor.execute(create_table_sql)
        print("users 表创建成功")
    conn.commit() # DDL 操作后最好提交

def crud_operations(conn):
    """演示 CRUD 操作"""
    print("\n--- 演示 CRUD 操作 ---")

    with conn.cursor() as cursor:
        # --- CREATE (创建) ---
        print("\n1. CREATE: 插入新用户")
        insert_sql = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
        users_to_insert = [
            ('Alice Smith', 'alice.s@example.com', 30),
            ('Bob Johnson', 'bob.j@example.com', 25),
            ('Charlie Brown', 'charlie.b@example.com', 35)
        ]
        try:
            # executemany 用于批量插入
            affected_rows = cursor.executemany(insert_sql, users_to_insert)
            conn.commit()
            print(f"成功插入 {affected_rows} 条记录")
        except pymysql.Error as err:
            print(f"插入失败: {err}")
            conn.rollback()

        # --- READ (读取) ---
        print("\n2. READ: 查询所有用户")
        select_all_sql = "SELECT id, name, email, age FROM users"
        cursor.execute(select_all_sql)
        all_users = cursor.fetchall()
        if all_users:
            print("查询结果:")
            for user in all_users:
                print(f"  ID: {user['id']}, 姓名: {user['name']}, 邮箱: {user['email']}, 年龄: {user['age']}")
        else:
            print("表中没有数据")

        print("\n3. READ: 查询特定用户 (例如: Bob Johnson)")
        select_one_sql = "SELECT id, name, email, age FROM users WHERE name = %s"
        cursor.execute(select_one_sql, ('Bob Johnson',))
        bob = cursor.fetchone()
        if bob:
            print(f"查询到 Bob: ID: {bob['id']}, 姓名: {bob['name']}, 邮箱: {bob['email']}, 年龄: {bob['age']}")
        else:
            print("未找到名为 Bob Johnson 的用户")

        # --- UPDATE (更新) ---
        print("\n4. UPDATE: 更新 Bob 的年龄")
        update_sql = "UPDATE users SET age = %s WHERE name = %s"
        try:
            new_age = 26
            affected_rows = cursor.execute(update_sql, (new_age, 'Bob Johnson'))
            conn.commit()
            if affected_rows > 0:
                print(f"成功更新 Bob 的年龄为 {new_age}")
                # 验证更新
                cursor.execute(select_one_sql, ('Bob Johnson',))
                updated_bob = cursor.fetchone()
                print(f"  更新后 Bob 的信息: ID: {updated_bob['id']}, 年龄: {updated_bob['age']}")
            else:
                print("未找到 Bob 或年龄未改变")
        except pymysql.Error as err:
            print(f"更新失败: {err}")
            conn.rollback()

        # --- DELETE (删除) ---
        print("\n5. DELETE: 删除 Charlie Brown")
        delete_sql = "DELETE FROM users WHERE name = %s"
        try:
            affected_rows = cursor.execute(delete_sql, ('Charlie Brown',))
            conn.commit()
            if affected_rows > 0:
                print("成功删除 Charlie Brown")
                # 验证删除
                cursor.execute(select_all_sql)
                remaining_users = cursor.fetchall()
                print("删除后的用户列表:")
                for user in remaining_users:
                    print(f"  ID: {user['id']}, 姓名: {user['name']}")
            else:
                print("未找到 Charlie Brown")
        except pymysql.Error as err:
            print(f"删除失败: {err}")
            conn.rollback()

def cleanup(conn):
    """清理创建的表"""
    print("\n--- 清理环境 --- ")
    with conn.cursor() as cursor:
        try:
            cursor.execute("DROP TABLE IF EXISTS users;")
            conn.commit()
            print("表 'users' 已删除")
        except pymysql.Error as err:
            print(f"删除表 'users' 时出错: {err}")
    print("清理完成")

if __name__ == "__main__":
    print("开始执行 pymysql CRUD 演示脚本")
    print("请确保 MySQL 服务正在运行，并已正确配置 db_config 中的用户名、密码、主机和数据库")
    print(f"将尝试连接到数据库: {db_config.get('database', '未指定')}")

    connection = create_connection()

    if connection:
        try:
            # 准备环境
            create_sample_table(connection)

            # 执行 CRUD 操作
            crud_operations(connection)

            print("\n演示完成！")

        except Exception as e:
            print(f"\n发生意外错误: {e}")
            # 发生错误时也尝试回滚未提交的事务
            try:
                connection.rollback()
                print("已执行最终回滚 (如果需要)")
            except pymysql.Error as rb_err:
                print(f"回滚时出错: {rb_err}")
        finally:
            # 清理本次运行创建的对象
            print("\n执行最终清理...")
            cleanup(connection)
            print("\n关闭数据库连接")
            connection.close()
    else:
        print("\n未能连接到数据库，脚本终止。请检查配置和 MySQL 服务状态。")

    print("\n提示: 要运行此脚本，您需要先安装 pymysql 库:")
    print("pip install pymysql")