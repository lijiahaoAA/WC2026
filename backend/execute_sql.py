import pg8000

def execute_scripts():
    print("正在连接 PostgreSQL...")
    try:
        conn = pg8000.connect(user="postgres", password="002505@Zx", host="127.0.0.1", port=5432, database="postgres")
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 读取并执行 database_init.sql
        print("正在执行建表脚本 database_init.sql...")
        with open('../database_init.sql', 'rb') as f:
            init_sql = f.read().decode('utf-8', errors='ignore')
        cursor.execute(init_sql)
        print("建表成功！")
        
        # 读取并执行 data_insert_2026.sql
        print("正在执行数据导入脚本 data_insert_2026.sql...")
        with open('../data_insert_2026.sql', 'rb') as f:
            insert_sql = f.read().decode('utf-8', errors='ignore')
        cursor.execute(insert_sql)
        print("数据导入成功！")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    execute_scripts()
