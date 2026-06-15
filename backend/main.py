from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv
from model_config import (
    get_available_models, get_model_params, get_all_model_configs,
    save_model_config, delete_model_config, test_model_connectivity
)
from data_collector import (
    sync_all, save_manual_result, get_match_context_with_live_data
)
from llm_client import call_llm

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
    """获取比赛上下文（增强版：含真实比赛数据和伤病信息）"""
    return get_match_context_with_live_data(team1_name, team2_name)

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


def extract_short_answer(text, field_name):
    """
    从模型输出中提取简短答案。
    思考模型（MiMo/DeepSeek）会返回推理过程，需要提取最终结论。
    短字段控制在50字以内，给出明确结论。
    """
    if not text:
        return text

    # 去掉思考过程标签（MiMo/DeepSeek 格式）
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # 去掉 markdown 格式符号
    text = re.sub(r'\*\*|__|~~|`', '', text)

    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if not lines:
        return text

    def limit(text, maxlen=50):
        """截断并确保有结论"""
        text = text.strip()
        if len(text) <= maxlen:
            return text
        # 在 maxlen 附近找标点断句
        for i in range(min(maxlen, len(text)), max(maxlen - 15, 0), -1):
            if text[i] in '。！？，；.!?;,':
                return text[:i + 1]
        return text[:maxlen]

    if field_name == 'score':
        # 匹配比分格式：2:1、1-1、2：0 等
        for line in reversed(lines):
            m = re.search(r'(\d+)\s*[:：\-]\s*(\d+)', line)
            if m:
                return f"{m.group(1)}:{m.group(2)}"
        return limit(lines[-1], 20)

    elif field_name == 'total_goals':
        # 匹配进球数格式：3球、2-3球、总进球3等
        for line in reversed(lines):
            m = re.search(r'(\d+)\s*[-~至]?\s*(\d+)\s*球', line)
            if m:
                return f"{m.group(1)}-{m.group(2)}球"
            m = re.search(r'(\d+)\s*球', line)
            if m:
                return f"{m.group(1)}球"
        return limit(lines[-1], 20)

    elif field_name == 'red_cards':
        # 从后往前找含关键词的行，取结论
        for line in reversed(lines):
            if any(kw in line for kw in ['红牌', '概率', '张', '低', '高', '中', '无', '有']):
                return limit(line, 50)
        return limit(lines[-1], 50)

    elif field_name == 'penalties':
        for line in reversed(lines):
            if any(kw in line for kw in ['点球', '概率', '低', '高', '中', '无', '有', '大战']):
                return limit(line, 50)
        return limit(lines[-1], 50)

    else:
        # advice 等长文本，去掉思考过程后返回全部
        return text


def check_or_upsert_prediction(req, field_name, prompt_addition, max_tokens, model_id="default", model_cfg=None):
    """
    单字段预测（支持多模型）。
    model_id: 缓存 key，默认 "default"
    model_cfg: 若提供则用 llm_client 调用指定模型，否则用默认 call_qwen
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if not req.force_refresh:
            cur.execute(f"SELECT {field_name} FROM match_predictions WHERE team1 = %s AND team2 = %s AND model_id = %s",
                        (req.team1_name, req.team2_name, model_id))
            row = cur.fetchone()
            if row and row[field_name]:
                cur.close()
                conn.close()
                return {"status": "success", "data": row[field_name]}

        context = get_match_context(req.team1_name, req.team2_name)
        prompt = context + prompt_addition

        if model_cfg:
            messages = [
                {"role": "system", "content": "你是资深的足球预测专家和精算师。请严格按要求输出最终结论，不要输出推理过程，不要任何前缀和标点。"},
                {"role": "user", "content": prompt}
            ]
            result = call_llm(model_cfg['provider'], model_cfg['api_key'], model_cfg['base_url'],
                              model_cfg['model'], messages, max_tokens=max_tokens, temperature=0.7)
        else:
            result = call_qwen(prompt, max_tokens)

        # 后处理：从思考模型输出中提取简短答案
        result = extract_short_answer(result, field_name)

        # 保存到数据库（ON CONFLICT 现在基于 team1, team2, model_id）
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO match_predictions (team1, team2, model_id, {field_name}, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (team1, team2, model_id) DO UPDATE SET {field_name} = EXCLUDED.{field_name}, updated_at = CURRENT_TIMESTAMP
        """, (req.team1_name, req.team2_name, model_id, result))
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


# ============================================================
# 多模型预测 API
# ============================================================

@app.get("/api/models")
def list_models():
    """返回所有已配置且 API_KEY 非空的模型列表"""
    return {"models": get_available_models()}


PREDICTION_FIELDS = [
    ("score",       "请预测本场比赛的最终比分。要求：只直接输出比分结果（例如：2:1 或 1:1），不要输出任何其他废话或解释。", 100),
    ("total_goals", "请预测本场比赛的总进球数。要求：只直接输出结果（例如：3球 或 2-3球），不要输出任何其他废话。", 100),
    ("red_cards",   "请预测本场比赛出现红牌的概率或数量预警。要求：用非常简短的一句话直接描述（例如：红牌概率低，或预计1张红牌），不要废话。", 200),
    ("penalties",   "请预测本场比赛出现点球或进入点球大战的概率。要求：用简短的一两句话直接描述，不要废话。", 200),
    ("advice",      "请给出详细的专家投注建议（结合基本面、六维能力雷达图、让球盘等，字数500字左右）。直接输出文本，不要包含任何前缀或Markdown代码块格式。", 2000),
]


class MultiPredictionRequest(BaseModel):
    team1_name: str
    team2_name: str
    model_ids: list[str]
    force_refresh: bool = False


@app.post("/api/predict/multi")
def predict_multi(req: MultiPredictionRequest):
    """多模型并行预测：对每个模型分别调用 5 个预测维度"""
    results = {}

    def predict_for_model(model_id):
        cfg = get_model_params(model_id)
        if not cfg:
            return model_id, {"status": "error", "message": f"模型 {model_id} 未配置"}
        model_result = {}
        for field_name, prompt_addition, max_tokens in PREDICTION_FIELDS:
            fake_req = type('Req', (), {
                'team1_name': req.team1_name,
                'team2_name': req.team2_name,
                'force_refresh': req.force_refresh
            })()
            resp = check_or_upsert_prediction(fake_req, field_name, prompt_addition, max_tokens,
                                              model_id=model_id, model_cfg=cfg)
            model_result[field_name] = resp.get("data", resp.get("message", "错误"))
        return model_id, model_result

    with ThreadPoolExecutor(max_workers=min(len(req.model_ids), 5)) as executor:
        futures = [executor.submit(predict_for_model, mid) for mid in req.model_ids]
        for f in futures:
            mid, result = f.result()
            results[mid] = result

    return {"status": "success", "results": results}


@app.post("/api/predict/aggregate")
def predict_aggregate(req: MultiPredictionRequest):
    """
    对多模型结果做规则投票聚合（不调用 LLM）。
    先获取各模型结果，再做多数投票 / 拼接。
    """
    # 先获取各模型结果（复用 multi 逻辑）
    multi_resp = predict_multi(req)
    if multi_resp.get("status") != "success":
        return multi_resp

    model_results = multi_resp["results"]

    # --- 比分投票 ---
    scores = [r.get("score", "") for r in model_results.values() if r.get("score") and r.get("score") != "分析失败"]
    final_score = _vote_text(scores)

    # --- 总进球投票 ---
    goals = [r.get("total_goals", "") for r in model_results.values() if r.get("total_goals") and r.get("total_goals") != "分析失败"]
    final_goals = _vote_text(goals)

    # --- 红牌投票 ---
    reds = [r.get("red_cards", "") for r in model_results.values() if r.get("red_cards") and r.get("red_cards") != "分析失败"]
    final_red_cards = _vote_text(reds)

    # --- 点球投票 ---
    pens = [r.get("penalties", "") for r in model_results.values() if r.get("penalties") and r.get("penalties") != "分析失败"]
    final_penalties = _vote_text(pens)

    # --- 投注建议拼接 ---
    advices = []
    for mid, r in model_results.items():
        adv = r.get("advice", "")
        if adv and adv not in ("分析失败", "请求错误"):
            model_name = mid
            for m in get_available_models():
                if m['id'] == mid:
                    model_name = m['name']
                    break
            advices.append(f"【{model_name}】\n{adv}")
    final_advice = "\n\n".join(advices) if advices else "暂无建议"

    return {
        "status": "success",
        "data": {
            "final_score": final_score,
            "final_goals": final_goals,
            "final_red_cards": final_red_cards,
            "final_penalties": final_penalties,
            "final_advice": final_advice,
            "model_count": len(model_results),
            "model_details": model_results,
        }
    }


def _vote_text(texts):
    """从多个文本结果中取众数；若无众数则取第一个"""
    if not texts:
        return "-"
    from collections import Counter
    counter = Counter(texts)
    most_common = counter.most_common(1)
    if most_common:
        return most_common[0][0]
    return texts[0]


# ============================================================
# 模型配置管理 API
# ============================================================

@app.get("/api/config/models")
def get_model_configs():
    """获取所有模型配置（API Key 脱敏）"""
    return {"models": get_all_model_configs()}


class SaveModelRequest(BaseModel):
    model_id: str = "new"
    name: str
    provider: str = "openai"
    api_key: str = ""
    base_url: str
    model: str


@app.post("/api/config/models")
def save_model(req: SaveModelRequest):
    """保存模型配置到 .env"""
    try:
        new_id = save_model_config(
            model_id=req.model_id,
            name=req.name,
            provider=req.provider,
            api_key=req.api_key,
            base_url=req.base_url,
            model_name=req.model
        )
        return {"status": "success", "model_id": new_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class DeleteModelRequest(BaseModel):
    model_id: str


@app.post("/api/config/models/delete")
def delete_model(req: DeleteModelRequest):
    """从 .env 中删除模型配置"""
    try:
        delete_model_config(req.model_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class TestModelRequest(BaseModel):
    model_id: str


@app.post("/api/config/models/test")
def test_model(req: TestModelRequest):
    """测试模型连通性"""
    success, message = test_model_connectivity(req.model_id)
    return {"status": "success" if success else "error", "message": message}


# ============================================================
# 历史预测查询 API
# ============================================================

@app.get("/api/predictions/history")
def get_prediction_history(team_name: str = None):
    """
    查询历史预测结果。
    - 不传 team_name：返回所有预测记录
    - 传 team_name：模糊搜索包含该球队的所有预测记录
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if team_name:
            cur.execute("""
                SELECT team1, team2, model_id, score, total_goals, red_cards, penalties, advice, updated_at
                FROM match_predictions
                WHERE team1 LIKE %s OR team2 LIKE %s
                ORDER BY updated_at DESC
            """, (f'%{team_name}%', f'%{team_name}%'))
        else:
            cur.execute("""
                SELECT team1, team2, model_id, score, total_goals, red_cards, penalties, advice, updated_at
                FROM match_predictions
                ORDER BY updated_at DESC
            """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # 按 (team1, team2) 分组，每个比赛聚合多个模型结果
        matches = {}
        for row in rows:
            key = f"{row['team1']} vs {row['team2']}"
            if key not in matches:
                matches[key] = {
                    'team1': row['team1'],
                    'team2': row['team2'],
                    'updated_at': str(row['updated_at']),
                    'models': {}
                }
            model_id = row['model_id'] or 'default'
            matches[key]['models'][model_id] = {
                'score': row['score'],
                'total_goals': row['total_goals'],
                'red_cards': row['red_cards'],
                'penalties': row['penalties'],
                'advice': row['advice'],
            }

        return {"status": "success", "data": list(matches.values())}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/predictions/history/{team1}/{team2}")
def get_match_prediction(team1: str, team2: str):
    """查询指定比赛的所有模型预测结果"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT model_id, score, total_goals, red_cards, penalties, advice, updated_at
            FROM match_predictions
            WHERE team1 = %s AND team2 = %s
            ORDER BY model_id
        """, (team1, team2))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        results = {}
        for row in rows:
            mid = row['model_id'] or 'default'
            results[mid] = {
                'score': row['score'],
                'total_goals': row['total_goals'],
                'red_cards': row['red_cards'],
                'penalties': row['penalties'],
                'advice': row['advice'],
            }

        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/schedule/all")
def get_schedule_all():
    """返回所有赛程，附带比赛结果和预测缓存状态"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.group_name, m.match_date, m.match_time, m.team1_name, m.team2_name, m.stadium, m.status
            FROM matches m ORDER BY m.id ASC
        """)
        rows = cur.fetchall()

        # 查询已有预测的比赛
        cur.execute("SELECT DISTINCT team1, team2 FROM match_predictions")
        predicted = set()
        for row in cur.fetchall():
            predicted.add((row[0], row[1]))

        # 查询比赛结果
        cur.execute("SELECT match_id, team1_score, team2_score FROM match_results")
        results_map = {}
        for row in cur.fetchall():
            results_map[row[0]] = {"team1_score": row[1], "team2_score": row[2]}

        schedule = []
        for row in rows:
            match_id = row[0]
            has_prediction = (row[4], row[5]) in predicted
            result = results_map.get(match_id)
            schedule.append({
                "id": match_id,
                "group": row[1], "date": row[2], "time": row[3],
                "team1": row[4], "team2": row[5], "stadium": row[6],
                "status": row[7],
                "has_prediction": has_prediction,
                "team1_score": result["team1_score"] if result else None,
                "team2_score": result["team2_score"] if result else None,
            })
        cur.close()
        conn.close()
        return schedule
    except Exception as e:
        print("Error:", e)
        return []


# ============================================================
# 数据同步 API
# ============================================================

@app.post("/api/data/sync")
def trigger_sync():
    """手动触发比赛数据同步（多数据源自动切换）"""
    try:
        result = sync_all()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class ManualResultRequest(BaseModel):
    team1: str
    team2: str
    score1: int
    score2: int
    events: list = []


@app.post("/api/data/manual_result")
def add_manual_result(req: ManualResultRequest):
    """手动录入比赛结果"""
    try:
        match_id = save_manual_result(req.team1, req.team2, req.score1, req.score2, req.events)
        return {"status": "success", "match_id": match_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/data/status")
def get_sync_status():
    """获取数据同步状态"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM match_results")
        result_count = cur.fetchone()[0]
        cur.execute("SELECT MAX(fetched_at) FROM match_results")
        last_sync = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM player_injuries WHERE status = 'out'")
        injury_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM player_match_stats")
        stats_count = cur.fetchone()[0]
        cur.close()
        conn.close()

        # 检查各数据源 Key 配置状态
        from data_collector import get_config
        sources = {
            "thesportsdb": True,  # 永远可用
            "football_data": bool(get_config("football_data_key")),
            "api_football": bool(get_config("api_football_key") or os.getenv("API_FOOTBALL_KEY")),
        }

        return {
            "status": "success",
            "data": {
                "matches_synced": result_count,
                "last_sync": str(last_sync) if last_sync else None,
                "active_injuries": injury_count,
                "player_stats_count": stats_count,
                "sources": sources,
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


class ApiKeyRequest(BaseModel):
    key: str


@app.post("/api/data/api_key")
def save_api_key(req: ApiKeyRequest):
    """保存 API-Football Key"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_config (key, value, updated_at) VALUES ('api_football_key', %s, CURRENT_TIMESTAMP)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """, (req.key,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/data/football_data_key")
def save_football_data_key(req: ApiKeyRequest):
    """保存 football-data.org Key"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_config (key, value, updated_at) VALUES ('football_data_key', %s, CURRENT_TIMESTAMP)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """, (req.key,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10086)
