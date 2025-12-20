# 第19节: MySQL存储过程进阶
# 内容: 存储过程的参数、分支流程与循环结构、游标

import mysql.connector

# 创建数据库连接
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="your_database"
    )

# 1. 带参数的存储过程示例
def create_procedure_with_params():
    conn = create_connection()
    cursor = conn.cursor()
    
    # 创建一个带输入输出参数的存储过程
    procedure = """
    CREATE PROCEDURE calculate_bonus(
        IN employee_id INT,
        IN base_salary DECIMAL(10,2),
        OUT bonus DECIMAL(10,2)
    )
    BEGIN
        DECLARE performance_score DECIMAL(3,2);
        SELECT score INTO performance_score FROM employee_performance WHERE id = employee_id;
        SET bonus = base_salary * performance_score;
    END
    """
    cursor.execute(procedure)
    conn.close()

# 2. 分支流程示例
def create_procedure_with_condition():
    conn = create_connection()
    cursor = conn.cursor()
    
    # 创建一个带条件判断的存储过程
    procedure = """
    CREATE PROCEDURE evaluate_performance(
        IN score INT
    )
    BEGIN
        IF score >= 90 THEN
            SELECT '优秀' AS result;
        ELSEIF score >= 80 THEN
            SELECT '良好' AS result;
        ELSE
            SELECT '一般' AS result;
        END IF;
    END
    """
    cursor.execute(procedure)
    conn.close()

# 3. 循环结构示例
def create_procedure_with_loop():
    conn = create_connection()
    cursor = conn.cursor()
    
    # 创建一个带循环的存储过程
    procedure = """
    CREATE PROCEDURE generate_numbers(
        IN n INT
    )
    BEGIN
        DECLARE i INT DEFAULT 1;
        DECLARE result VARCHAR(1000) DEFAULT '';
        
        WHILE i <= n DO
            SET result = CONCAT(result, i, ',');
            SET i = i + 1;
        END WHILE;
        
        SELECT result;
    END
    """
    cursor.execute(procedure)
    conn.close()

# 4. 游标使用示例
def create_procedure_with_cursor():
    conn = create_connection()
    cursor = conn.cursor()
    
    # 创建一个使用游标的存储过程
    procedure = """
    CREATE PROCEDURE process_employees()
    BEGIN
        DECLARE done INT DEFAULT FALSE;
        DECLARE emp_id INT;
        DECLARE emp_name VARCHAR(100);
        
        DECLARE emp_cursor CURSOR FOR 
            SELECT id, name FROM employees;
            
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
        
        OPEN emp_cursor;
        
        read_loop: LOOP
            FETCH emp_cursor INTO emp_id, emp_name;
            IF done THEN
                LEAVE read_loop;
            END IF;
            
            # 处理每个员工的数据
            UPDATE employees 
            SET processed = TRUE 
            WHERE id = emp_id;
        END LOOP;
        
        CLOSE emp_cursor;
    END
    """
    cursor.execute(procedure)
    conn.close()

# 主函数调用示例
if __name__ == "__main__":
    try:
        create_procedure_with_params()
        create_procedure_with_condition()
        create_procedure_with_loop()
        create_procedure_with_cursor()
        print("所有存储过程创建成功！")
    except mysql.connector.Error as err:
        print(f"错误: {err}")
