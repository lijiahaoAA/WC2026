import psycopg2
import json

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "002505@Zx",
    "host": "localhost",
    "port": 5432
}

def init_detailed_tables():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # 扩展 teams 表以包含更详细的信息
    cur.execute("""
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS total_value VARCHAR(50);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS avg_age DECIMAL(4,1);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS coach VARCHAR(100);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS formation VARCHAR(50);
        ALTER TABLE teams ADD COLUMN IF NOT EXISTS logo_url TEXT;
    """)
    
    # 创建详细球员表
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
    
    conn.commit()
    cur.close()
    conn.close()

def insert_mexico_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # 1. 更新墨西哥队基础信息
    cur.execute("""
        UPDATE teams 
        SET 
            total_value = '2.2亿欧元',
            avg_age = 26.6,
            coach = '哈维尔·阿吉雷',
            formation = '4-2-3-1',
            logo_url = 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f6/Mexico_national_football_team_logo.svg/800px-Mexico_national_football_team_logo.svg.png'
        WHERE name = '墨西哥'
        RETURNING id;
    """)
    team_id = cur.fetchone()[0]
    
    # 2. 清理旧数据（如果有）
    cur.execute("DELETE FROM players_detailed WHERE team_id = %s", (team_id,))
    
    # 3. 录入 26 人名单数据
    players = [
        # 门将
        ("吉列尔莫·奥乔亚", 40, "门将", "AEL利马索尔", True, "五朝元老，精神支柱"),
        ("何塞·兰格尔", 26, "门将", "瓜达拉哈拉", False, "主力替补，脚下技术好"),
        ("卡洛斯·阿切维多", 28, "门将", "桑托斯拉古纳", False, ""),
        # 后卫
        ("豪尔赫·桑切斯", 28, "后卫", "塞萨洛尼基", True, "右路攻防均衡"),
        ("伊塞尔·雷耶斯", 27, "后卫", "美洲队", False, "中卫改右后卫，稳健"),
        ("塞萨尔·蒙特斯", 29, "后卫", "莫斯科火车头", True, "主力中卫，防空强"),
        ("约翰·巴斯克斯", 27, "后卫", "热那亚", True, "主力中卫，出球稳"),
        ("赫苏斯·加利亚多", 31, "后卫", "托卢卡", True, "主力左后卫，助攻强"),
        ("马特奥·查韦斯", 22, "后卫", "阿尔克马尔", False, "左路替补，年轻有活力"),
        # 中场
        ("埃德森·阿尔瓦雷斯", 28, "中场", "费内巴切", True, "队长，后腰核心，拦截+出球"),
        ("路易斯·罗莫", 31, "中场", "瓜达拉哈拉", True, "后腰，防守屏障"),
        ("阿尔瓦罗·菲达尔戈", 27, "中场", "皇家贝蒂斯", False, "中场串联，技术流"),
        ("布莱恩·古铁雷斯", 22, "中场", "瓜达拉哈拉", True, "进攻中场，创造力强"),
        ("奥贝德·巴尔加斯", 22, "中场", "马德里竞技", False, "年轻后腰，跑动积极"),
        ("希尔韦托·莫拉", 17, "中场", "蒂华纳", False, "最年轻国脚，天才新星"),
        ("埃里克·里拉", 26, "中场", "蓝十字", False, "中场工兵，覆盖大"),
        ("路易斯·查韦斯", 30, "中场", "莫斯科迪纳摩", False, "远射强，定位球主罚者"),
        ("奥贝林·皮内达", 30, "中场", "雅典AEK", False, "边前卫，内切得分"),
        # 前锋
        ("劳尔·希门尼斯", 35, "前锋", "富勒姆", False, "主力中锋，英超经验丰富"),
        ("圣地亚哥·希门尼斯", 24, "前锋", "AC米兰", True, "主力前锋，意甲高效射手"),
        ("亚历克西斯·维加", 27, "前锋", "托卢卡", True, "左边锋，速度快"),
        ("罗伯托·阿尔瓦拉多", 27, "前锋", "瓜达拉哈拉", True, "右边锋，突破强"),
        ("塞萨尔·韦尔塔", 25, "前锋", "安德莱赫特", False, "中锋/边锋，替补杀手"),
        ("胡利安·奎尼奥内斯", 28, "前锋", "沙特联赛", False, "金靴得主，嗅觉灵敏"),
        ("阿曼多·冈萨雷斯", 23, "前锋", "瓜达拉哈拉", False, "年轻中锋，潜力大"),
        ("吉列尔莫·马丁内斯", 28, "前锋", "美洲狮", False, "高中锋，战术支点")
    ]
    
    cur.executemany("""
        INSERT INTO players_detailed 
        (team_id, name, age, position, club, is_starter, description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [(team_id, p[0], p[1], p[2], p[3], p[4], p[5]) for p in players])
    
    conn.commit()
    print("墨西哥队 26 人名单数据录入成功！")
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_detailed_tables()
    insert_mexico_data()
