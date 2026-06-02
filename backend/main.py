from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量

app = FastAPI(title="世界杯预测协助系统 API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接函数
def get_db_connection():
    # 使用环境变量获取敏感信息，若未配置则使用默认值或抛错
    db_password = os.getenv("DB_PASSWORD", "002505@Zx")
    return psycopg2.connect(user="postgres", password=db_password, host="127.0.0.1", port=5432, database="postgres")

@app.get("/")
def read_root():
    return {"message": "世界杯预测协助系统后端服务运行正常，请访问前端地址 (如 http://localhost:10087) 或 API 文档 (http://localhost:10086/docs)"}

@app.get("/api/schedule")
def get_schedule():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT group_name, match_date, match_time, team1_name, team2_name, stadium FROM matches ORDER BY id ASC")
        rows = cursor.fetchall()
        schedule = []
        for row in rows:
            schedule.append({
                "group": row[0],
                "date": row[1],
                "time": row[2],
                "team1": row[3],
                "team2": row[4],
                "stadium": row[5]
            })
        conn.close()
        return schedule
    except Exception as e:
        print("从数据库读取赛程失败:", e)
        return []

@app.get("/api/teams")
def get_teams():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, country_code, fifa_ranking, group_name, coach FROM teams ORDER BY id;")
        rows = cursor.fetchall()
        teams = []
        for row in rows:
            teams.append({
                "id": row[0], "name": row[1], "country_code": row[2],
                "fifa_ranking": row[3], "group_name": row[4], "coach": row[5]
            })
        conn.close()
        return teams
    except Exception as e:
        # 如果数据库还没准备好，返回空列表或者错误信息
        print("数据库连接或查询错误:", e)
        return []

@app.get("/api/players")
def get_players(team_id: int = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if team_id:
            cursor.execute("SELECT id, name, position, age, jersey_number, is_key_player FROM players WHERE team_id = %s ORDER BY id;", (team_id,))
        else:
            cursor.execute("SELECT p.id, p.name, t.name, p.position, p.age, p.jersey_number, p.is_key_player FROM players p JOIN teams t ON p.team_id = t.id ORDER BY p.id LIMIT 100;")
        rows = cursor.fetchall()
        players = []
        for row in rows:
            if team_id:
                players.append({"id": row[0], "name": row[1], "position": row[2], "age": row[3], "jersey_number": row[4], "is_key_player": row[5]})
            else:
                players.append({"id": row[0], "name": row[1], "team_name": row[2], "position": row[3], "age": row[4], "jersey_number": row[5], "is_key_player": row[6]})
        conn.close()
        return players
    except Exception as e:
        print("数据库连接或查询错误:", e)
        return []

@app.get("/api/team/{team_name}")
def get_team_info(team_name: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. 获取球队基础信息
        cur.execute("""
            SELECT id, name, country_code, group_name, fifa_ranking, 
                   total_value, avg_age, coach, formation, logo_url, founded, city, stadium, capacity
            FROM teams 
            WHERE name = %s
        """, (team_name,))
        team = cur.fetchone()
        
        if not team:
            return {"status": "error", "message": "Team not found"}
            
        # 2. 获取该球队的球员名单
        cur.execute("""
            SELECT id, name, age, position, club, is_starter, description, height, weight, preferred_foot, birth_date, overall_rating, stats, honors, transfers, injuries
            FROM players_detailed
            WHERE team_id = %s
            ORDER BY 
                CASE position 
                    WHEN '门将' THEN 1 
                    WHEN '后卫' THEN 2 
                    WHEN '中场' THEN 3 
                    WHEN '前锋' THEN 4 
                    ELSE 5 
                END,
                is_starter DESC
        """, (team['id'],))
        players = cur.fetchall()
        
        team['players'] = players
        
        return {"status": "success", "data": team}
        
    except Exception as e:
        print(f"Error fetching team info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

class PredictionRequest(BaseModel):
    team1_id: int
    team2_id: int

@app.post("/api/predict")
def predict_match(req: PredictionRequest):
    # 此处为数据分析与胜率测算核心逻辑
    # 基于 FIFA 排名和简单的核心球员加成进行概率预测
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, fifa_ranking FROM teams WHERE id = %s", (req.team1_id,))
        t1 = cursor.fetchone()
        cursor.execute("SELECT name, fifa_ranking FROM teams WHERE id = %s", (req.team2_id,))
        t2 = cursor.fetchone()
        conn.close()

        if not t1 or not t2:
            raise HTTPException(status_code=404, detail="球队未找到")
            
        t1_name, t1_rank = t1[0], t1[1]
        t2_name, t2_rank = t2[0], t2[1]

        # 简单的算法：排名越靠前（数字越小），实力越强
        # 假设第一名实力分是 100，每降一名减少 1 分
        t1_power = max(100 - t1_rank + 10, 10)
        t2_power = max(100 - t2_rank + 10, 10)
        
        total_power = t1_power + t2_power
        t1_win_rate = round((t1_power / total_power) * 100, 2)
        t2_win_rate = round((t2_power / total_power) * 100, 2)
        draw_rate = round(100 - t1_win_rate - t2_win_rate, 2) # 平局概率，简单算法下不考虑平局或者设为很小，这里直接二分胜率

        # 稍微调整加入平局概率
        draw_rate = 20.0
        t1_win_rate = round(t1_win_rate * 0.8, 2)
        t2_win_rate = round(t2_win_rate * 0.8, 2)

        return {
            "team1": t1_name,
            "team2": t2_name,
            "team1_win_rate": f"{t1_win_rate}%",
            "draw_rate": f"{draw_rate}%",
            "team2_win_rate": f"{t2_win_rate}%",
            "analysis": f"基于客观 FIFA 排名测算，{t1_name}(排名{t1_rank}) 对阵 {t2_name}(排名{t2_rank})。请注意足球比赛具有偶然性，此测算仅供参考，不作为买彩票的绝对依据。"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LLMPredictionRequest(BaseModel):
    team1_name: str
    team2_name: str
    force_refresh: bool = False

client = OpenAI(
    api_key=os.getenv("ALIYUN_API_KEY", "your_default_key_here"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_match_context(team1_name, team2_name):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 提取主队数据
    cur.execute("SELECT * FROM teams WHERE name = %s", (team1_name,))
    t1 = cur.fetchone()
    t1_players = []
    if t1:
        cur.execute("SELECT name, position, age, club, is_starter, description, overall_rating, stats FROM players_detailed WHERE team_id = %s ORDER BY overall_rating DESC NULLS LAST", (t1['id'],))
        t1_players = cur.fetchall()

    # 提取客队数据
    cur.execute("SELECT * FROM teams WHERE name = %s", (team2_name,))
    t2 = cur.fetchone()
    t2_players = []
    if t2:
        cur.execute("SELECT name, position, age, club, is_starter, description, overall_rating, stats FROM players_detailed WHERE team_id = %s ORDER BY overall_rating DESC NULLS LAST", (t2['id'],))
        t2_players = cur.fetchall()
        
    cur.close()
    conn.close()

    def format_team_prompt(t, players):
        p_text = f"【{t['name']}】\n"
        p_text += f"FIFA排名：{t.get('fifa_ranking')}\n"
        p_text += f"主教练：{t.get('coach')}\n"
        p_text += f"阵型：{t.get('formation')}\n"
        p_text += f"身价：{t.get('total_value')}\n"
        p_text += f"平均年龄：{t.get('avg_age')}\n"
        p_text += "部分核心球员(按综合评分降序)：\n"
        for p in players[:6]:
            stats_str = ""
            if p.get('stats'):
                stats_str = " | ".join([f"{k}:{v}" for k, v in p['stats'].items()])
            p_text += f"- {p['name']} ({p['position']}, 评分: {p.get('overall_rating')}) : {stats_str}\n"
        p_text += "\n"
        return p_text
        
    context = f"你是一个专业的足球赛事分析师和彩票精算师。请基于以下详细的真实数据，对 {team1_name} vs {team2_name} 的比赛进行定性分析。\n\n"
    if t1: context += format_team_prompt(t1, t1_players)
    if t2: context += format_team_prompt(t2, t2_players)
    return context

def call_qwen(prompt, max_tokens=500):
    completion = client.chat.completions.create(
        model="qwen3.7-max",
        messages=[
            {"role": "system", "content": "你是资深的足球预测专家和精算师，严格按要求输出，不废话，不要任何前缀和标点。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content.strip()

def check_or_upsert_prediction(req, field_name, prompt_addition, max_tokens):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if not req.force_refresh:
            cur.execute(f"SELECT {field_name} FROM match_predictions WHERE team1 = %s AND team2 = %s", (req.team1_name, req.team2_name))
            row = cur.fetchone()
            if row and row[field_name]:
                cur.close()
                conn.close()
                return {"status": "success", "data": row[field_name]}
        
        context = get_match_context(req.team1_name, req.team2_name)
        prompt = context + prompt_addition
        result = call_qwen(prompt, max_tokens)
        
        # 保存到数据库
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO match_predictions (team1, team2, {field_name}, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (team1, team2) DO UPDATE SET {field_name} = EXCLUDED.{field_name}, updated_at = CURRENT_TIMESTAMP
        """, (req.team1_name, req.team2_name, result))
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/predict/score")
def predict_score(req: LLMPredictionRequest):
    return check_or_upsert_prediction(req, "score", "请预测本场比赛的最终比分。要求：只直接输出比分结果（例如：2:1 或 1:1），不要输出任何其他废话或解释。", 20)

@app.post("/api/predict/goals")
def predict_goals(req: LLMPredictionRequest):
    return check_or_upsert_prediction(req, "total_goals", "请预测本场比赛的总进球数。要求：只直接输出结果（例如：3球 或 2-3球），不要输出任何其他废话。", 20)

@app.post("/api/predict/red_cards")
def predict_red_cards(req: LLMPredictionRequest):
    return check_or_upsert_prediction(req, "red_cards", "请预测本场比赛出现红牌的概率或数量预警。要求：用非常简短的一句话直接描述（例如：红牌概率低，或预计1张红牌），不要废话。", 50)

@app.post("/api/predict/penalties")
def predict_penalties(req: LLMPredictionRequest):
    return check_or_upsert_prediction(req, "penalties", "请预测本场比赛出现点球或进入点球大战的概率。要求：用简短的一两句话直接描述，不要废话。", 100)

@app.post("/api/predict/advice")
def predict_advice(req: LLMPredictionRequest):
    return check_or_upsert_prediction(req, "advice", "请给出详细的专家投注建议（结合基本面、六维能力雷达图、让球盘等，字数500字左右）。直接输出文本，不要包含任何前缀或Markdown代码块格式。", 1500)

if __name__ == "__main__":
    import uvicorn
    # 使用五位数端口 10086
    uvicorn.run(app, host="0.0.0.0", port=10086)
