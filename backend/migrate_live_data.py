# -*- coding: utf-8 -*-
"""数据库迁移：新增比赛结果、球员表现、伤病跟踪表，扩展 players_detailed 字段"""
import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}


def migrate():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # 1. 比赛结果表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            team1_name VARCHAR(100),
            team2_name VARCHAR(100),
            team1_score INTEGER,
            team2_score INTEGER,
            status VARCHAR(20) DEFAULT 'finished',
            half_time_score VARCHAR(20),
            events JSONB,
            stats JSONB,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(match_id)
        )
    """)
    print("[OK] match_results table")

    # 2. 球员单场表现表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_match_stats (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players_detailed(id),
            match_id INTEGER REFERENCES matches(id),
            minutes_played INTEGER,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_card BOOLEAN DEFAULT FALSE,
            rating DECIMAL(3,1),
            events JSONB,
            UNIQUE(player_id, match_id)
        )
    """)
    print("[OK] player_match_stats table")

    # 3. 伤病跟踪表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_injuries (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players_detailed(id),
            player_name VARCHAR(100),
            team_name VARCHAR(100),
            injury_type VARCHAR(100),
            status VARCHAR(20) DEFAULT 'out',
            expected_return VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        )
    """)
    print("[OK] player_injuries table")

    # 4. 扩展 players_detailed
    columns_to_add = [
        ("current_form", "VARCHAR(20)"),
        ("tournament_goals", "INTEGER DEFAULT 0"),
        ("tournament_assists", "INTEGER DEFAULT 0"),
        ("tournament_yellow", "INTEGER DEFAULT 0"),
        ("tournament_red", "INTEGER DEFAULT 0"),
        ("is_injured", "BOOLEAN DEFAULT FALSE"),
        ("injury_detail", "TEXT"),
    ]
    for col_name, col_type in columns_to_add:
        cur.execute(f"ALTER TABLE players_detailed ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
    print("[OK] players_detailed columns extended")

    # 5. API 配置表（存储 API-Football Key 等）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS api_config (
            key VARCHAR(100) PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] api_config table")

    conn.commit()
    cur.close()
    conn.close()
    print("\nMigration complete!")


if __name__ == "__main__":
    migrate()
