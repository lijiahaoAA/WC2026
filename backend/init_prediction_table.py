import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def init_prediction_table():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS match_predictions (
            id SERIAL PRIMARY KEY,
            team1 VARCHAR(100),
            team2 VARCHAR(100),
            total_goals VARCHAR(100),
            red_cards VARCHAR(100),
            penalties VARCHAR(200),
            score VARCHAR(100),
            advice TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team1, team2)
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("match_predictions 表创建成功")

if __name__ == "__main__":
    init_prediction_table()
