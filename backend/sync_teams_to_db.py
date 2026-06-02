import psycopg2
import json

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def sync_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # 确保扩展了 teams 表结构
    cur.execute("""
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS total_value VARCHAR(50);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS avg_age DECIMAL(4,1);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS coach VARCHAR(100);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS formation VARCHAR(50);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS logo_url TEXT;
    """)
    
    # 确保创建详细球员表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players_detailed (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            name VARCHAR(100) NOT NULL,
            age INTEGER,
            position VARCHAR(50),
            club VARCHAR(100),
            is_starter BOOLEAN DEFAULT FALSE,
            description TEXT
        )
    """)
    
    with open('../球队信息.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for team_data in data:
        team_name = team_data.get('球队名称')
        
        # 提取其他字段
        total_value = team_data.get('球队总身价', '')
        avg_age_str = team_data.get('平均年龄', '').replace('岁', '')
        try:
            avg_age = float(avg_age_str)
        except:
            avg_age = 0.0
            
        formation = team_data.get('惯用阵型', '')
        coach = team_data.get('教练团队', {}).get('主教练', '')
        
        # 1. 更新球队基础信息
        cur.execute("""
            UPDATE teams 
            SET 
                total_value = %s,
                avg_age = %s,
                coach = %s,
                formation = %s
            WHERE name = %s
            RETURNING id;
        """, (total_value, avg_age, coach, formation, team_name))
        
        row = cur.fetchone()
        if not row:
            print(f"警告：数据库中未找到球队 {team_name}，跳过更新。")
            continue
            
        team_id = row[0]
        
        # 2. 清理该球队旧数据
        cur.execute("DELETE FROM players_detailed WHERE team_id = %s", (team_id,))
        
        # 3. 提取球员并准备插入
        players = []
        expected_starters = team_data.get('预计首发阵容', {})
        starters_names = []
        for pos, names_str in expected_starters.items():
            # 简单分割（如 "卡瓦哈尔、拉波尔特" -> ["卡瓦哈尔", "拉波尔特"]）
            # 或者处理包含空格或、的名字
            for name in names_str.replace('、', ',').replace(' ', ',').split(','):
                if name.strip():
                    starters_names.append(name.strip())
                    
        # 处理球员名单
        squad_data = team_data.get('球员名单', {})
        for position_cat, player_list in squad_data.items():
            for p_str in player_list:
                # 格式如 "乌奈·西蒙（毕尔巴鄂竞技）"
                club = ""
                name = p_str
                if '（' in p_str and '）' in p_str:
                    parts = p_str.split('（')
                    name = parts[0].strip()
                    club = parts[1].replace('）', '').strip()
                elif '(' in p_str and ')' in p_str:
                    parts = p_str.split('(')
                    name = parts[0].strip()
                    club = parts[1].replace(')', '').strip()
                
                # 检查是否为首发
                is_starter = False
                for s_name in starters_names:
                    # 部分匹配，如 s_name "西蒙" 匹配 "乌奈·西蒙"
                    if s_name in name or name in s_name:
                        is_starter = True
                        break
                        
                players.append((team_id, name, 25, position_cat, club, is_starter, ""))
                
        if players:
            cur.executemany("""
                INSERT INTO players_detailed 
                (team_id, name, age, position, club, is_starter, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, players)
            
    conn.commit()
    print(f"成功将 {len(data)} 支球队数据同步到数据库！")
    cur.close()
    conn.close()

if __name__ == "__main__":
    sync_data()
