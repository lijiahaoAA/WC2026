# -*- coding: utf-8 -*-
"""
比赛数据采集模块 — 多数据源冗余
依次尝试多个数据源，直到有数据返回：
  1. TheSportsDB（免费，无需 Key）
  2. football-data.org（免费，需 Key）
  3. API-Football / RapidAPI（免费100次/天，需 Key）
  4. 手动录入（兜底）
"""
import json
import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "002505@Zx"),
    "host": "localhost",
    "port": 5432
}

# ============================================================
# 中英文队名映射
# ============================================================
TEAM_NAME_MAP = {
    '墨西哥': 'Mexico', '南非': 'South Africa', '韩国': 'South Korea', '捷克': 'Czech Republic',
    '加拿大': 'Canada', '波黑': 'Bosnia and Herzegovina', '卡塔尔': 'Qatar', '瑞士': 'Switzerland',
    '巴西': 'Brazil', '摩洛哥': 'Morocco', '海地': 'Haiti', '苏格兰': 'Scotland',
    '美国': 'USA', '巴拉圭': 'Paraguay', '澳大利亚': 'Australia', '土耳其': 'Turkey',
    '德国': 'Germany', '库拉索': 'Curacao', '科特迪瓦': 'Ivory Coast', '厄瓜多尔': 'Ecuador',
    '荷兰': 'Netherlands', '日本': 'Japan', '瑞典': 'Sweden', '突尼斯': 'Tunisia',
    '比利时': 'Belgium', '埃及': 'Egypt', '伊朗': 'Iran', '新西兰': 'New Zealand',
    '西班牙': 'Spain', '佛得角': 'Cape Verde', '沙特阿拉伯': 'Saudi Arabia', '乌拉圭': 'Uruguay',
    '法国': 'France', '塞内加尔': 'Senegal', '伊拉克': 'Iraq', '挪威': 'Norway',
    '阿根廷': 'Argentina', '阿尔及利亚': 'Algeria', '奥地利': 'Austria', '约旦': 'Jordan',
    '葡萄牙': 'Portugal', '刚果民主共和国': 'DR Congo', '乌兹别克斯坦': 'Uzbekistan', '哥伦比亚': 'Colombia',
    '英格兰': 'England', '克罗地亚': 'Croatia', '加纳': 'Ghana', '巴拿马': 'Panama',
}
EN_TO_CN = {v: k for k, v in TEAM_NAME_MAP.items()}


def get_db():
    return psycopg2.connect(**DB_PARAMS)


def get_config(key, default=""):
    """从数据库 api_config 表读取配置"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT value FROM api_config WHERE key = %s", (key,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else default
    except:
        return default


# ============================================================
# 数据源 1：TheSportsDB（免费，无需 Key）
# ============================================================
THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"
# 世界杯2026 赛事ID（TheSportsDB）
WC_LEAGUE_ID_THESPORTSDB = 4466


def _thesportsdb_fetch_fixtures():
    """从 TheSportsDB 拉取世界杯已完赛比赛"""
    results = []
    try:
        # 尝试多个 round 获取比赛
        for round_num in range(1, 10):
            url = f"{THESPORTSDB_BASE}/eventsround.php?id={WC_LEAGUE_ID_THESPORTSDB}&r={round_num}&s=2025-2026"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            events = data.get("events")
            if not events:
                break
            for evt in events:
                home = evt.get("strHomeTeam", "")
                away = evt.get("strAwayTeam", "")
                home_score = evt.get("intHomeScore")
                away_score = evt.get("intAwayScore")
                status = evt.get("strStatus", "")
                if home_score is not None and away_score is not None:
                    results.append({
                        "source": "thesportsdb",
                        "home_team_en": home,
                        "away_team_en": away,
                        "home_score": int(home_score) if str(home_score).isdigit() else None,
                        "away_score": int(away_score) if str(away_score).isdigit() else None,
                        "status": status or "finished",
                        "date": evt.get("dateEvent", ""),
                        "events": [],
                    })
    except Exception as e:
        print(f"[TheSportsDB] Error: {e}")
    return results


def _thesportsdb_fetch_events(fixture_id):
    """从 TheSportsDB 拉取比赛事件"""
    try:
        url = f"{THESPORTSDB_BASE}/lookupevent.php?id={fixture_id}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        events = data.get("events", [])
        return events[0] if events else None
    except:
        return None


# ============================================================
# 数据源 2：football-data.org（免费，需 Key）
# ============================================================
FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"


def _footballdata_fetch_fixtures():
    """从 football-data.org 拉取世界杯比赛"""
    key = get_config("football_data_key")
    if not key:
        return []

    results = []
    try:
        headers = {"X-Auth-Token": key}
        url = f"{FOOTBALL_DATA_BASE}/competitions/WC/matches?status=FINISHED"
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        for match in data.get("matches", []):
            home = match.get("homeTeam", {}).get("name", "")
            away = match.get("awayTeam", {}).get("name", "")
            score = match.get("score", {}).get("fullTime", {})
            results.append({
                "source": "football-data",
                "home_team_en": home,
                "away_team_en": away,
                "home_score": score.get("home"),
                "away_score": score.get("away"),
                "status": "finished",
                "date": match.get("utcDate", ""),
                "events": [],
                "fixture_id": match.get("id"),
            })
    except Exception as e:
        print(f"[football-data] Error: {e}")
    return results


# ============================================================
# 数据源 3：API-Football / RapidAPI（需 Key）
# ============================================================
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")


def _apifootball_fetch_fixtures():
    """从 API-Football 拉取世界杯已完赛比赛"""
    key = get_config("api_football_key") or os.getenv("API_FOOTBALL_KEY", "")
    if not key:
        return []

    results = []
    try:
        url = f"https://{API_FOOTBALL_HOST}/fixtures"
        headers = {"x-apisports-key": key}
        params = {"league": 1, "season": 2026, "status": "FT"}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        data = resp.json()
        for fix in data.get("response", []):
            teams = fix.get("teams", {})
            goals = fix.get("goals", {})
            fixture_info = fix.get("fixture", {})
            results.append({
                "source": "api-football",
                "home_team_en": teams.get("home", {}).get("name", ""),
                "away_team_en": teams.get("away", {}).get("name", ""),
                "home_score": goals.get("home"),
                "away_score": goals.get("away"),
                "status": fixture_info.get("status", {}).get("short", "FT"),
                "date": fixture_info.get("date", ""),
                "events": [],
                "fixture_id": fixture_info.get("id"),
            })
    except Exception as e:
        print(f"[API-Football] Error: {e}")
    return results


def _apifootball_fetch_events(fixture_id):
    """从 API-Football 拉取比赛事件"""
    key = get_config("api_football_key") or os.getenv("API_FOOTBALL_KEY", "")
    if not key:
        return []
    try:
        url = f"https://{API_FOOTBALL_HOST}/fixtures/events"
        headers = {"x-apisports-key": key}
        resp = requests.get(url, headers=headers, params={"fixture": fixture_id}, timeout=15)
        return resp.json().get("response", [])
    except:
        return []


# ============================================================
# 统一数据源调度
# ============================================================

DATA_SOURCES = [
    ("TheSportsDB", _thesportsdb_fetch_fixtures),
    ("football-data.org", _footballdata_fetch_fixtures),
    ("API-Football", _apifootball_fetch_fixtures),
]


def fetch_all_fixtures():
    """
    依次尝试所有数据源，直到有数据返回。
    返回 (results: list, source_name: str, error: str|None)
    """
    errors = []
    for name, fetcher in DATA_SOURCES:
        try:
            results = fetcher()
            if results:
                print(f"[DataCollector] {name} returned {len(results)} matches")
                return results, name, None
            else:
                errors.append(f"{name}: 无数据")
        except Exception as e:
            errors.append(f"{name}: {e}")

    return [], "none", "所有数据源均无数据: " + "; ".join(errors)


# ============================================================
# 数据写入
# ============================================================

def _find_match_id(cur, home_cn, away_cn):
    """在 matches 表中查找对应比赛"""
    cur.execute("SELECT id FROM matches WHERE team1_name = %s AND team2_name = %s", (home_cn, away_cn))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("SELECT id FROM matches WHERE team1_name = %s AND team2_name = %s", (away_cn, home_cn))
    row = cur.fetchone()
    if row:
        return row[0]
    return None


def save_fixtures(fixtures):
    """保存比赛结果到数据库"""
    conn = get_db()
    cur = conn.cursor()
    saved = 0

    for fix in fixtures:
        home_en = fix.get("home_team_en", "")
        away_en = fix.get("away_team_en", "")
        home_cn = EN_TO_CN.get(home_en, home_en)
        away_cn = EN_TO_CN.get(away_en, away_en)

        # 也尝试中文名直接匹配
        if home_cn == home_en:
            # 可能已经是中文名
            for cn in TEAM_NAME_MAP:
                if cn in home_en or home_en in cn:
                    home_cn = cn
                    break
        if away_cn == away_en:
            for cn in TEAM_NAME_MAP:
                if cn in away_en or away_en in cn:
                    away_cn = cn
                    break

        match_id = _find_match_id(cur, home_cn, away_cn)
        if not match_id:
            # 创建新的赛程记录
            cur.execute("""
                INSERT INTO matches (group_name, match_date, match_time, team1_name, team2_name, stadium, status)
                VALUES (%s, %s, '', %s, %s, '', 'finished') RETURNING id
            """, (f"数据源:{fix.get('source','')}", fix.get("date", ""), home_cn, away_cn))
            match_id = cur.fetchone()[0]

        # 更新赛程状态
        cur.execute("UPDATE matches SET status = 'finished' WHERE id = %s", (match_id,))

        # 保存比赛结果
        events_json = json.dumps(fix.get("events", []), ensure_ascii=False, default=str)
        cur.execute("""
            INSERT INTO match_results (match_id, team1_name, team2_name, team1_score, team2_score, status, events)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id) DO UPDATE SET
                team1_score = EXCLUDED.team1_score,
                team2_score = EXCLUDED.team2_score,
                status = EXCLUDED.status,
                events = EXCLUDED.events,
                fetched_at = CURRENT_TIMESTAMP
        """, (match_id, home_cn, away_cn, fix.get("home_score"), fix.get("away_score"),
              fix.get("status", "finished"), events_json))
        saved += 1

    conn.commit()
    cur.close()
    conn.close()
    return saved


def save_manual_result(team1, team2, score1, score2, events=None):
    """手动录入比赛结果"""
    conn = get_db()
    cur = conn.cursor()

    match_id = _find_match_id(cur, team1, team2)
    if not match_id:
        cur.execute("""
            INSERT INTO matches (group_name, match_date, match_time, team1_name, team2_name, stadium, status)
            VALUES ('手动录入', %s, '', %s, %s, '', 'finished') RETURNING id
        """, (datetime.now().strftime('%Y年%m月%d日'), team1, team2))
        match_id = cur.fetchone()[0]
    else:
        cur.execute("UPDATE matches SET status = 'finished' WHERE id = %s", (match_id,))

    cur.execute("""
        INSERT INTO match_results (match_id, team1_name, team2_name, team1_score, team2_score, status, events)
        VALUES (%s, %s, %s, %s, %s, 'finished', %s)
        ON CONFLICT (match_id) DO UPDATE SET
            team1_score = EXCLUDED.team1_score,
            team2_score = EXCLUDED.team2_score,
            events = EXCLUDED.events,
            fetched_at = CURRENT_TIMESTAMP
    """, (match_id, team1, team2, score1, score2,
          json.dumps(events or [], ensure_ascii=False)))

    conn.commit()
    cur.close()
    conn.close()
    return match_id


# ============================================================
# 一键同步
# ============================================================

def sync_all():
    """一键同步：拉取数据 → 保存 → 返回结果"""
    results = {"source": "", "fixtures": 0, "errors": []}

    fixtures, source, err = fetch_all_fixtures()
    if err:
        results["errors"].append(err)
        return results

    results["source"] = source
    results["fixtures"] = save_fixtures(fixtures)

    return results


# ============================================================
# 增强版预测上下文
# ============================================================

def get_match_context_with_live_data(team1_name, team2_name):
    """获取增强版比赛上下文（含真实比赛数据和伤病信息）"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    def format_team(team_name):
        cur.execute("SELECT * FROM teams WHERE name = %s", (team_name,))
        t = cur.fetchone()
        if not t:
            return f"【{team_name}】数据不足\n"

        cur.execute("""
            SELECT name, position, age, club, is_starter, overall_rating, stats,
                   current_form, tournament_goals, tournament_assists, is_injured, injury_detail
            FROM players_detailed WHERE team_id = %s ORDER BY overall_rating DESC NULLS LAST
        """, (t['id'],))
        players = cur.fetchall()

        text = f"【{team_name}】\n"
        text += f"FIFA排名：{t.get('fifa_ranking')} | 主教练：{t.get('coach')} | 阵型：{t.get('formation') or '未知'}\n"
        text += f"总身价：{t.get('total_value') or '未知'} | 平均年龄：{t.get('avg_age') or '未知'}\n"

        # 真实比赛结果
        cur.execute("""
            SELECT mr.team1_name, mr.team2_name, mr.team1_score, mr.team2_score
            FROM match_results mr
            WHERE mr.team1_name = %s OR mr.team2_name = %s
            ORDER BY mr.fetched_at DESC LIMIT 5
        """, (team_name, team_name))
        recent = cur.fetchall()
        if recent:
            wins, draws, losses = 0, 0, 0
            goals_for, goals_against = 0, 0
            results_list = []
            for r in recent:
                is_home = r['team1_name'] == team_name
                gf = r['team1_score'] if is_home else r['team2_score']
                ga = r['team2_score'] if is_home else r['team1_score']
                if gf is None or ga is None:
                    continue
                goals_for += gf
                goals_against += ga
                opp = r['team2_name'] if is_home else r['team1_name']
                results_list.append(f"{gf}-{ga} vs {opp}")
                if gf > ga:
                    wins += 1
                elif gf == ga:
                    draws += 1
                else:
                    losses += 1
            if results_list:
                text += f"世界杯战绩：{wins}胜{draws}平{losses}负 | 进{goals_for}球失{goals_against}球\n"
                text += f"近期比赛：{' / '.join(results_list)}\n"

        text += "\n核心球员（按评分降序）：\n"
        for p in players[:8]:
            parts = [f"{p['name']} ({p['position']}, 评分{p.get('overall_rating')})"]
            if p.get('tournament_goals') or p.get('tournament_assists'):
                parts.append(f"世界杯:{p.get('tournament_goals',0)}球{p.get('tournament_assists',0)}助")
            if p.get('current_form'):
                form_map = {'excellent': '优秀', 'good': '良好', 'average': '一般', 'poor': '低迷'}
                parts.append(f"状态:{form_map.get(p['current_form'], p['current_form'])}")
            if p.get('is_injured'):
                parts.append(f"⚠伤病:{p.get('injury_detail', '未知')}")
            if p.get('stats'):
                stats_str = " | ".join([f"{k}:{v}" for k, v in p['stats'].items()])
                parts.append(f"[{stats_str}]")
            text += "- " + " | ".join(parts) + "\n"

        # 伤病汇总
        injured = [p for p in players if p.get('is_injured')]
        if injured:
            text += "\n伤病名单：\n"
            for p in injured:
                text += f"- {p['name']}：{p.get('injury_detail', '未知伤病')}\n"

        text += "\n"
        return text

    context = "你是一个专业的足球赛事分析师和彩票精算师。请基于以下包含真实世界杯比赛数据的信息进行分析。\n\n"
    context += format_team(team1_name)
    context += format_team(team2_name)

    cur.close()
    conn.close()
    return context
