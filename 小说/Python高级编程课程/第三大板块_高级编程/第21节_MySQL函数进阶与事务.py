# 第21节: MySQL函数进阶与事务
# 内容: MySQL函数运用、事务特性与运用

import mysql.connector
from mysql.connector import errorcode
import decimal # 用于精确比较DECIMAL类型

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

def execute_query(conn, query, data=None, commit=True):
    """执行SQL查询 (简化版，事务控制在调用处处理)"""
    cursor = conn.cursor()
    try:
        if data:
            cursor.execute(query, data)
            print(f"执行成功 (带参数): {query[:60]}...")
        else:
            cursor.execute(query)
            print(f"执行成功: {query[:60]}...")
        if commit:
            conn.commit()
        return cursor # 返回游标以便获取结果
    except mysql.connector.Error as err:
        print(f"执行失败: {err}")
        print(f"失败的查询: {query}")
        # 不在此处回滚，让调用者决定
        # conn.rollback()
        raise err # 抛出异常，让调用者处理
    finally:
        # 不在此处关闭游标，调用者需要读取结果
        # cursor.close()
        pass

def create_sample_tables_for_transactions(conn):
    """为事务演示创建账户表"""
    print("\n--- 创建账户表示例 ---")
    create_accounts_table = """
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INT AUTO_INCREMENT PRIMARY KEY,
        account_holder VARCHAR(255) NOT NULL,
        balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0)
    ) ENGINE=InnoDB;
    """
    execute_query(conn, create_accounts_table)
    # 清空旧数据
    execute_query(conn, "DELETE FROM accounts")
    # 插入初始数据
    execute_query(conn, "INSERT INTO accounts (account_holder, balance) VALUES (%s, %s)", ('Alice', 1000.00))
    execute_query(conn, "INSERT INTO accounts (account_holder, balance) VALUES (%s, %s)", ('Bob', 500.00))
    print("账户表创建并初始化完成")

def demonstrate_transactions(conn):
    """
    演示数据库事务处理 (转账操作)
    事务特性 (ACID):
    - 原子性 (Atomicity): 事务作为一个整体执行，要么全部成功，要么全部失败回滚。
    - 一致性 (Consistency): 事务执行前后，数据库状态从一个一致状态转移到另一个一致状态。
    - 隔离性 (Isolation): 并发执行的事务之间互不干扰。
    - 持久性 (Durability): 一旦事务提交，其结果永久保存在数据库中。
    """
    print("\n--- 演示事务处理 (银行转账) ---")
    print("事务特性 (ACID): 原子性, 一致性, 隔离性, 持久性")

    cursor = conn.cursor(dictionary=True)

    # 初始状态
    print("\n初始账户余额:")
    cursor.execute("SELECT account_holder, balance FROM accounts WHERE account_holder IN ('Alice', 'Bob')")
    for row in cursor.fetchall():
        print(f"  {row['account_holder']}: {row['balance']}")

    # 场景1: 成功转账 (Alice -> Bob 100元)
    print("\n场景1: 成功转账 (Alice -> Bob 100元)")
    transfer_amount = decimal.Decimal('100.00')
    try:
        # 开始事务 (mysql-connector-python 默认自动提交，需显式关闭或手动管理)
        # conn.autocommit = False # 关闭自动提交，或者在每次操作后不调用 commit()
        # 或者使用 conn.start_transaction()
        conn.start_transaction()
        print("  开始事务...")

        # 1. 扣除 Alice 余额
        print(f"  尝试扣除 Alice 余额 {transfer_amount}")
        update_alice_sql = "UPDATE accounts SET balance = balance - %s WHERE account_holder = 'Alice' AND balance >= %s"
        cursor.execute(update_alice_sql, (transfer_amount, transfer_amount))
        if cursor.rowcount == 0:
            raise ValueError("Alice 余额不足或账户不存在")
        print("  Alice 余额扣除成功")

        # 2. 增加 Bob 余额
        print(f"  尝试增加 Bob 余额 {transfer_amount}")
        update_bob_sql = "UPDATE accounts SET balance = balance + %s WHERE account_holder = 'Bob'"
        cursor.execute(update_bob_sql, (transfer_amount,))
        if cursor.rowcount == 0:
            raise ValueError("Bob 账户不存在")
        print("  Bob 余额增加成功")

        # 提交事务
        conn.commit()
        print("  事务提交成功")

    except (mysql.connector.Error, ValueError) as err:
        print(f"  转账失败: {err}")
        print("  执行事务回滚...")
        conn.rollback()
        print("  事务已回滚")
    finally:
        # conn.autocommit = True # 如果修改过，恢复默认
        pass

    # 查看转账后结果
    print("\n转账后账户余额:")
    cursor.execute("SELECT account_holder, balance FROM accounts WHERE account_holder IN ('Alice', 'Bob')")
    for row in cursor.fetchall():
        print(f"  {row['account_holder']}: {row['balance']}")

    # 场景2: 转账失败 (Alice -> Bob 10000元，余额不足)
    print("\n场景2: 转账失败 (Alice 余额不足，尝试转 10000元)")
    failed_transfer_amount = decimal.Decimal('10000.00')
    try:
        conn.start_transaction()
        print("  开始事务...")

        # 1. 尝试扣除 Alice 余额
        print(f"  尝试扣除 Alice 余额 {failed_transfer_amount}")
        update_alice_sql = "UPDATE accounts SET balance = balance - %s WHERE account_holder = 'Alice' AND balance >= %s"
        cursor.execute(update_alice_sql, (failed_transfer_amount, failed_transfer_amount))
        if cursor.rowcount == 0:
            raise ValueError("Alice 余额不足或账户不存在") # 这里会触发异常
        print("  Alice 余额扣除成功 (理论上不会执行到这里)")

        # 2. 增加 Bob 余额 (如果上面成功，这里也会执行)
        update_bob_sql = "UPDATE accounts SET balance = balance + %s WHERE account_holder = 'Bob'"
        cursor.execute(update_bob_sql, (failed_transfer_amount,))
        print("  Bob 余额增加成功 (理论上不会执行到这里)")

        conn.commit()
        print("  事务提交成功 (理论上不会执行到这里)")

    except (mysql.connector.Error, ValueError) as err:
        print(f"  转账失败: {err}")
        print("  执行事务回滚...")
        conn.rollback()
        print("  事务已回滚")
    finally:
        pass

    # 查看失败转账后的结果 (应与场景1结束后一致)
    print("\n失败转账尝试后账户余额 (应无变化):")
    cursor.execute("SELECT account_holder, balance FROM accounts WHERE account_holder IN ('Alice', 'Bob')")
    for row in cursor.fetchall():
        print(f"  {row['account_holder']}: {row['balance']}")

    cursor.close()

def drop_function_if_exists(conn, func_name):
    """如果函数存在则删除"""
    query = f"DROP FUNCTION IF EXISTS {func_name};"
    try:
        execute_query(conn, query)
        print(f"函数 '{func_name}' (如果存在) 已删除")
    except mysql.connector.Error as err:
        # 忽略函数不存在的错误
        if err.errno != errorcode.ER_SP_DOES_NOT_EXIST:
            print(f"删除函数 '{func_name}' 时出错: {err}")

def create_advanced_udf(conn):
    """创建更复杂的UDF：根据账户余额计算信用等级"""
    print("\n--- 创建进阶用户定义函数 (UDF) --- ")
    func_name = "get_credit_rating"
    drop_function_if_exists(conn, func_name)

    create_func_sql = f"""
    CREATE FUNCTION {func_name}(account_balance DECIMAL(15, 2))
    RETURNS VARCHAR(10)
    DETERMINISTIC
    BEGIN
        DECLARE credit_rating VARCHAR(10);
        IF account_balance >= 10000 THEN
            SET credit_rating = 'AAA';
        ELSEIF account_balance >= 5000 THEN
            SET credit_rating = 'AA';
        ELSEIF account_balance >= 1000 THEN
            SET credit_rating = 'A';
        ELSEIF account_balance >= 100 THEN
            SET credit_rating = 'B';
        ELSE
            SET credit_rating = 'C';
        END IF;
        RETURN credit_rating;
    END
    """
    try:
        # UDF 创建可能需要特殊处理多语句，但这里是单条 CREATE FUNCTION
        execute_query(conn, create_func_sql)
        print(f"函数 '{func_name}' 创建成功")
    except mysql.connector.Error as err:
        print(f"创建函数 '{func_name}' 失败: {err}")

def demonstrate_advanced_udf(conn):
    """演示进阶UDF的使用"""
    print("\n--- 演示进阶用户定义函数 (UDF) --- ")
    cursor = conn.cursor(dictionary=True)

    print("\n使用 UDF 查询账户信用等级:")
    query = """
    SELECT
        account_holder,
        balance,
        get_credit_rating(balance) AS credit_rating
    FROM accounts;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"  账户: {row['account_holder']}, 余额: {row['balance']}, 信用等级 (UDF计算): {row['credit_rating']}")
        else:
            print("没有账户数据可用于演示 UDF")
    except mysql.connector.Error as err:
        # 检查是否是函数不存在的错误
        if "get_credit_rating does not exist" in str(err):
             print(f"错误：函数 'get_credit_rating' 未成功创建或不存在。请检查 create_advanced_udf 函数的执行情况。")
        else:
            print(f"查询失败: {err}")
    finally:
        cursor.close()

def cleanup(conn):
    """清理创建的表和函数"""
    print("\n--- 清理环境 --- ")
    print("删除函数...")
    drop_function_if_exists(conn, "get_credit_rating")

    print("删除表...")
    try:
        execute_query(conn, "DROP TABLE IF EXISTS accounts;")
        print("表 'accounts' 已删除")
    except mysql.connector.Error as err:
        print(f"删除表 'accounts' 时出错: {err}")

    print("清理完成")


if __name__ == "__main__":
    print("开始执行 MySQL 函数进阶与事务演示脚本")
    print("请确保 MySQL 服务正在运行，并已正确配置 db_config 中的用户名、密码和主机")
    print(f"将尝试连接到数据库: {db_config.get('database', '未指定')}")

    connection = create_connection()

    if connection and connection.is_connected():
        try:
            # 准备环境 (事务演示)
            create_sample_tables_for_transactions(connection)

            # 演示事务
            demonstrate_transactions(connection)

            # 准备环境 (UDF演示 - 复用账户表)
            # 演示进阶UDF
            create_advanced_udf(connection)
            demonstrate_advanced_udf(connection)

            print("\n演示完成！")

        except Exception as e:
            print(f"\n发生意外错误: {e}")
        finally:
            # 清理本次运行创建的对象
            print("\n执行最终清理...")
            cleanup(connection)
            print("\n关闭数据库连接")
            connection.close()
    else:
        print("\n未能连接到数据库，脚本终止。请检查配置和 MySQL 服务状态。")