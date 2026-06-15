"""
WC2026 数据库一键初始化脚本
功能：创建表结构 + 导入48支球队 + 导入赛程 + 导入球员详细数据
"""
import json
import os
import glob
import psycopg2
from psycopg2.extras import Json

# winget 安装的 PostgreSQL 默认密码通常是 postgres
# 如果连接失败，请修改这里的密码
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "002505@Zx"),
    "host": "localhost",
    "port": 5432
}

def create_tables(cur):
    """创建所有必要的表"""
    print("[1/4] 创建表结构...")

    # 球队表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            country_code VARCHAR(10),
            fifa_ranking INTEGER,
            group_name VARCHAR(10),
            coach VARCHAR(100),
            total_value VARCHAR(50),
            avg_age DECIMAL(4,1),
            formation VARCHAR(50),
            logo_url TEXT,
            founded VARCHAR(20),
            city VARCHAR(100),
            stadium VARCHAR(200),
            capacity VARCHAR(20)
        )
    """)

    # 球员基础表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            name VARCHAR(100) NOT NULL,
            position VARCHAR(50),
            age INTEGER,
            jersey_number INTEGER,
            is_key_player BOOLEAN DEFAULT FALSE
        )
    """)

    # 球员详细表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players_detailed (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            name VARCHAR(100) NOT NULL,
            age INTEGER,
            position VARCHAR(50),
            club VARCHAR(100),
            is_starter BOOLEAN DEFAULT FALSE,
            description TEXT,
            height INTEGER,
            weight INTEGER,
            preferred_foot VARCHAR(20),
            birth_date VARCHAR(30),
            overall_rating INTEGER,
            stats JSONB,
            honors JSONB,
            transfers JSONB,
            injuries JSONB
        )
    """)

    # 赛程表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            group_name VARCHAR(20),
            match_date VARCHAR(30),
            match_time VARCHAR(10),
            team1_name VARCHAR(100),
            team2_name VARCHAR(100),
            stadium VARCHAR(200),
            status VARCHAR(20) DEFAULT 'upcoming'
        )
    """)

    # 预测缓存表（支持多模型）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS match_predictions (
            id SERIAL PRIMARY KEY,
            team1 VARCHAR(100) NOT NULL,
            team2 VARCHAR(100) NOT NULL,
            model_id VARCHAR(50) DEFAULT 'default',
            score TEXT,
            total_goals TEXT,
            red_cards TEXT,
            penalties TEXT,
            advice TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team1, team2, model_id)
        )
    """)

    print("  [OK] 表结构创建完成")


def insert_teams(cur):
    """插入48支2026世界杯球队"""
    print("[2/4] 导入48支球队数据...")

    # 先清空旧数据
    cur.execute("TRUNCATE TABLE players_detailed RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE players RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE matches RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE teams RESTART IDENTITY CASCADE")

    groups_data = {
        'A': ['墨西哥', '南非', '韩国', '捷克'],
        'B': ['加拿大', '波黑', '卡塔尔', '瑞士'],
        'C': ['巴西', '摩洛哥', '海地', '苏格兰'],
        'D': ['美国', '巴拉圭', '澳大利亚', '土耳其'],
        'E': ['德国', '库拉索', '科特迪瓦', '厄瓜多尔'],
        'F': ['荷兰', '日本', '瑞典', '突尼斯'],
        'G': ['比利时', '埃及', '伊朗', '新西兰'],
        'H': ['西班牙', '佛得角', '沙特阿拉伯', '乌拉圭'],
        'I': ['法国', '塞内加尔', '伊拉克', '挪威'],
        'J': ['阿根廷', '阿尔及利亚', '奥地利', '约旦'],
        'K': ['葡萄牙', '刚果民主共和国', '乌兹别克斯坦', '哥伦比亚'],
        'L': ['英格兰', '克罗地亚', '加纳', '巴拿马']
    }

    mock_rankings = {
        '阿根廷': 1, '法国': 2, '巴西': 3, '英格兰': 4, '比利时': 5, '葡萄牙': 6, '荷兰': 7, '西班牙': 8,
        '克罗地亚': 10, '乌拉圭': 11, '哥伦比亚': 12, '美国': 13, '摩洛哥': 14, '墨西哥': 15, '德国': 16,
        '塞内加尔': 17, '日本': 18, '瑞士': 19, '伊朗': 20, '韩国': 22, '澳大利亚': 23, '奥地利': 25,
        '瑞典': 26, '突尼斯': 28, '阿尔及利亚': 30, '厄瓜多尔': 31, '埃及': 33, '土耳其': 35, '苏格兰': 39,
        '巴拉圭': 41, '挪威': 46, '加拿大': 48, '科特迪瓦': 49, '沙特阿拉伯': 53, '巴拉圭': 56, '南非': 58,
        '卡塔尔': 58, '伊拉克': 59, '加纳': 61, '佛得角': 65, '乌兹别克斯坦': 66, '刚果民主共和国': 67,
        '约旦': 70, '巴拿马': 44, '海地': 90, '库拉索': 91, '新西兰': 104, '波黑': 41, '捷克': 36
    }

    country_codes = {
        '阿根廷': 'ARG', '法国': 'FRA', '巴西': 'BRA', '英格兰': 'ENG', '比利时': 'BEL', '葡萄牙': 'POR',
        '荷兰': 'NED', '西班牙': 'ESP', '哥伦比亚': 'COL', '墨西哥': 'MEX', '乌拉圭': 'URU', '瑞士': 'SUI',
        '美国': 'USA', '德国': 'GER', '塞内加尔': 'SEN', '日本': 'JPN', '伊朗': 'IRN', '韩国': 'KOR',
        '澳大利亚': 'AUS', '奥地利': 'AUT', '瑞典': 'SWE', '突尼斯': 'TUN', '阿尔及利亚': 'ALG', '埃及': 'EGY',
        '土耳其': 'TUR', '厄瓜多尔': 'ECU', '苏格兰': 'SCO', '波黑': 'BIH', '捷克': 'CZE', '加拿大': 'CAN',
        '沙特阿拉伯': 'KSA', '科特迪瓦': 'CIV', '巴拉圭': 'PAR', '南非': 'RSA', '卡塔尔': 'QAT', '加纳': 'GHA',
        '伊拉克': 'IRQ', '乌兹别克斯坦': 'UZB', '巴拿马': 'PAN', '佛得角': 'CPV', '约旦': 'JOR', '海地': 'HAI',
        '库拉索': 'CUW', '新西兰': 'NZL', '刚果民主共和国': 'COD', '克罗地亚': 'CRO', '摩洛哥': 'MAR', '挪威': 'NOR'
    }

    team_id = 1
    team_name_to_id = {}
    for group_name, teams in groups_data.items():
        for team_name in teams:
            code = country_codes.get(team_name, 'UNK')
            rank = mock_rankings.get(team_name, 99)
            cur.execute(
                "INSERT INTO teams (id, name, country_code, fifa_ranking, group_name, coach) VALUES (%s, %s, %s, %s, %s, %s)",
                (team_id, team_name, code, rank, group_name, '待定')
            )
            team_name_to_id[team_name] = team_id
            team_id += 1

    print(f"  [OK] 已导入 {team_id - 1} 支球队")
    return team_name_to_id


def insert_schedule(cur):
    """导入赛程数据"""
    print("[3/4] 导入赛程数据...")
    schedule_path = os.path.join(os.path.dirname(__file__), 'schedule.json')
    if not os.path.exists(schedule_path):
        print("  [WARN] schedule.json 不存在，跳过赛程导入")
        return

    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    for match in schedule:
        cur.execute(
            "INSERT INTO matches (group_name, match_date, match_time, team1_name, team2_name, stadium, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (match['group'], match['date'], match['time'], match['team1'], match['team2'], match['stadium'], match.get('status', 'upcoming'))
        )

    print(f"  [OK] 已导入 {len(schedule)} 场比赛")


def insert_players(cur, team_name_to_id):
    """从 WorldCup2026_Teams 目录导入球员详细数据"""
    print("[4/4] 导入球员详细数据...")
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'WorldCup2026_Teams')
    json_files = glob.glob(os.path.join(base_dir, "**", "*.json"), recursive=True)

    total_players = 0
    teams_updated = 0

    for file_path in json_files:
        if file_path.endswith("teams_list.json"):
            continue

        team_name = os.path.basename(file_path).replace('.json', '')
        team_id = team_name_to_id.get(team_name)
        if not team_id:
            print(f"  [WARN] 未找到球队 {team_name}，跳过")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [ERR] 读取 {file_path} 失败: {e}")
            continue

        team_info = data.get("team_info", {})
        squad = data.get("squad", [])

        # 更新球队附加信息
        founded = str(team_info.get("founded", ""))
        city = team_info.get("city", "")
        stadium = team_info.get("stadium", "")
        capacity = str(team_info.get("capacity", ""))
        market_value = team_info.get("market_value", "")

        cur.execute("""
            UPDATE teams SET founded=%s, city=%s, stadium=%s, capacity=%s, total_value=%s
            WHERE id=%s
        """, (founded, city, stadium, capacity, market_value, team_id))

        # 提取教练名字
        coach_name = None
        for p in squad:
            if "教练" in p.get("position", ""):
                coach_name = p.get("name")
                break
        if coach_name:
            cur.execute("UPDATE teams SET coach=%s WHERE id=%s AND (coach IS NULL OR coach='待定')", (coach_name, team_id))

        teams_updated += 1

        # 插入球员
        for p in squad:
            name = p.get("name", "")
            if not name:
                continue
            position = p.get("position", "")
            if "教练" in position:
                continue

            age = p.get("age")
            height = p.get("height")
            if height is not None:
                try:
                    height = int(''.join(filter(str.isdigit, str(height))))
                except ValueError:
                    height = None

            weight = p.get("weight")
            if weight is not None:
                try:
                    weight = int(''.join(filter(str.isdigit, str(weight))))
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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                team_id, name, age, position, "", False,
                height, weight, preferred_foot, birth_date, overall_rating,
                Json(stats) if stats else None,
                Json(honors) if honors else None,
                Json(transfers) if transfers else None,
                Json(injuries) if injuries else None
            ))
            total_players += 1

        # 自动分配首发 (4-3-3)
        cur.execute("""
            WITH RankedPlayers AS (
                SELECT id, position,
                    ROW_NUMBER() OVER(PARTITION BY position ORDER BY overall_rating DESC NULLS LAST) as rn
                FROM players_detailed
                WHERE team_id = %s AND position != '教练'
            )
            UPDATE players_detailed SET is_starter = TRUE
            WHERE id IN (
                SELECT id FROM RankedPlayers
                WHERE (position = '门将' AND rn <= 1)
                   OR (position = '后卫' AND rn <= 4)
                   OR (position = '中场' AND rn <= 3)
                   OR (position = '前锋' AND rn <= 3)
            )
        """, (team_id,))

        # 补齐不足11人
        cur.execute("""
            UPDATE players_detailed SET is_starter = TRUE
            WHERE id IN (
                SELECT id FROM players_detailed
                WHERE team_id = %s AND position != '教练' AND is_starter = FALSE
                ORDER BY overall_rating DESC NULLS LAST
                LIMIT (11 - (SELECT COUNT(*) FROM players_detailed WHERE team_id = %s AND is_starter = TRUE))
            )
        """, (team_id, team_id))

    print(f"  [OK] 已更新 {teams_updated} 支球队，导入 {total_players} 名球员")


def main():
    print("=" * 50)
    print("  WC2026 数据库初始化")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        create_tables(cur)
        team_name_to_id = insert_teams(cur)
        insert_schedule(cur)
        insert_players(cur, team_name_to_id)

        conn.commit()

        # 验证
        cur.execute("SELECT COUNT(*) FROM teams")
        t = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM players_detailed")
        p = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM matches")
        m = cur.fetchone()[0]

        print("=" * 50)
        print(f"  [DONE] 初始化完成！")
        print(f"  球队: {t} 支 | 球员: {p} 名 | 赛程: {m} 场")
        print("=" * 50)

        cur.close()
        conn.close()
    except Exception as e:
        print(f"\n[ERR] 数据库连接失败: {e}")
        print("请确认 PostgreSQL 已启动，且密码正确。")
        print("当前连接参数:", {k: v for k, v in DB_PARAMS.items() if k != 'password'})
        raise


if __name__ == "__main__":
    main()
