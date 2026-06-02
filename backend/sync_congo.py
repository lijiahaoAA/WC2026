import json
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": "localhost",
    "port": 5432
}

def sync_congo():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    file_path = r"e:\工作\系统开发\sjb\WorldCup2026_Teams\Group_K\刚果民主共和国.json"
    team_name_in_db = "刚果（金）"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    team_info = data.get("team_info", {})
    squad = data.get("squad", [])
    
    founded = str(team_info.get("成立", team_info.get("founded_year", team_info.get("founded", ""))))
    city = team_info.get("城市", team_info.get("city", ""))
    stadium = team_info.get("主场", team_info.get("stadium", ""))
    capacity = str(team_info.get("容量", team_info.get("capacity", "")))
    market_value = team_info.get("市值", team_info.get("market_value", ""))
    
    cur.execute("""
        UPDATE teams 
        SET 
            founded = %s,
            city = %s,
            stadium = %s,
            capacity = %s,
            total_value = %s
        WHERE name = %s
        RETURNING id;
    """, (founded, city, stadium, capacity, market_value, team_name_in_db))
    
    row = cur.fetchone()
    if not row:
        print(f"Error: 找不到球队 {team_name_in_db}")
        return
        
    team_id = row[0]
    
    cur.execute("DELETE FROM players_detailed WHERE team_id = %s", (team_id,))
    
    total_players_inserted = 0
    for p in squad:
        name = p.get("name", "")
        if not name:
            continue
        position = p.get("position", "")
        
        if "教练" in position:
            cur.execute("""
                UPDATE teams SET coach = %s WHERE id = %s AND (coach IS NULL OR coach = '');
            """, (name, team_id))
            continue
            
        age = p.get("age")
        club = ""
        
        height_raw = p.get("height")
        height = None
        if height_raw is not None:
            try:
                height = int(''.join(filter(str.isdigit, str(height_raw))))
            except ValueError:
                height = None
                
        weight_raw = p.get("weight")
        weight = None
        if weight_raw is not None:
            try:
                weight = int(''.join(filter(str.isdigit, str(weight_raw))))
            except ValueError:
                weight = None
                
        preferred_foot = p.get("preferred_foot")
        birth_date = p.get("birth_date")
        overall_rating = p.get("overall_rating")
        
        stats = p.get("stats")
        honors = p.get("honors")
        transfers = p.get("transfers")
        injuries = p.get("injuries")
        
        cur.execute("""
            INSERT INTO players_detailed (
                team_id, name, age, position, club, is_starter, 
                height, weight, preferred_foot, birth_date, overall_rating, 
                stats, honors, transfers, injuries
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            team_id, name, age, position, club, False,
            height, weight, preferred_foot, birth_date, overall_rating,
            Json(stats) if stats else None, 
            Json(honors) if honors else None, 
            Json(transfers) if transfers else None, 
            Json(injuries) if injuries else None
        ))
        total_players_inserted += 1
        
    cur.execute("""
        UPDATE players_detailed 
        SET is_starter = TRUE 
        WHERE id IN (
            SELECT id FROM players_detailed 
            WHERE team_id = %s 
            ORDER BY overall_rating DESC NULLS LAST 
            LIMIT 11
        )
    """, (team_id,))

    conn.commit()
    cur.close()
    conn.close()
    print(f"成功导入 {team_name_in_db} (刚果民主共和国) 的数据！共插入 {total_players_inserted} 名球员。")

if __name__ == "__main__":
    sync_congo()
