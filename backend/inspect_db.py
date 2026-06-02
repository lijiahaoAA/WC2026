import psycopg2
import json

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def inspect_db():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("Tables:", tables)
    
    for table in tables:
        tname = table[0]
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{tname}'
        """)
        cols = cur.fetchall()
        print(f"Table {tname}:", cols)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_db()
