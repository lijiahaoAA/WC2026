import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def upgrade_db_schema():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    print("正在扩充 teams 表...")
    cur.execute("""
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS founded VARCHAR(50);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS city VARCHAR(100);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS stadium VARCHAR(100);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS capacity VARCHAR(50);
    """)
    
    print("正在扩充 players_detailed 表...")
    cur.execute("""
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS height INTEGER;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS weight INTEGER;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS preferred_foot VARCHAR(20);
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS birth_date VARCHAR(50);
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS overall_rating INTEGER;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS stats JSONB;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS honors JSONB;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS transfers JSONB;
        ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS injuries JSONB;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("表结构升级完成！")

if __name__ == "__main__":
    upgrade_db_schema()
