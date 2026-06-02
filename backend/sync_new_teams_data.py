import os
import glob
import json
import psycopg2
from psycopg2.extras import Json

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def sync_new_teams_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    base_dir = r"e:\工作\系统开发\sjb\WorldCup2026_Teams"
    json_files = glob.glob(os.path.join(base_dir, "**", "*.json"), recursive=True)
    
    total_teams_updated = 0
    total_players_inserted = 0
    
    for file_path in json_files:
        if file_path.endswith("teams_list.json"):
            continue
            
        team_name = os.path.basename(file_path).replace('.json', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
            
        team_info = data.get("team_info", {})
        squad = data.get("squad", [])
        
        # 1. 更新 teams 表的新字段
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
        """, (founded, city, stadium, capacity, market_value, team_name))
        
        row = cur.fetchone()
        if not row:
            print(f"警告: 数据库未找到球队 {team_name}，跳过该球队的详细数据插入。")
            continue
            
        team_id = row[0]
        total_teams_updated += 1
        
        # 2. 清理旧的球员数据并插入新数据
        cur.execute("DELETE FROM players_detailed WHERE team_id = %s", (team_id,))
        
        for p in squad:
            name = p.get("name", "")
            if not name:
                continue
            position = p.get("position", "")
            # 处理教练
            if "教练" in position:
                cur.execute("""
                    UPDATE teams SET coach = %s WHERE id = %s AND (coach IS NULL OR coach = '');
                """, (name, team_id))
                continue
                
            age = p.get("age")
            club = ""  # 数据结构中可能没有明确拆分俱乐部，暂时留空或从其他地方提取
            
            # 处理 height 和 weight 中可能包含的非数字字符 (如 "165cm", "60kg")
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
            
            # 根据 overall_rating 等猜测是否为首发，或者默认给 True（因为之前我们删除了数据，前端需要展示首发）
            # 新数据里没有 is_starter 标记，这里根据评分做一个粗略判断或者前 11 人为首发
            is_starter = False
            
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
                team_id, name, age, position, club, is_starter,
                height, weight, preferred_foot, birth_date, overall_rating,
                Json(stats) if stats else None, 
                Json(honors) if honors else None, 
                Json(transfers) if transfers else None, 
                Json(injuries) if injuries else None
            ))
            total_players_inserted += 1
            
        # 简单逻辑：将前11个位置不是教练的球员设为首发
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
    print(f"数据迁移成功！更新了 {total_teams_updated} 支球队信息，插入了 {total_players_inserted} 名球员的详细数据。")

if __name__ == "__main__":
    sync_new_teams_data()
