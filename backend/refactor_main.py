import os

file_path = r"e:\工作\系统开发\sjb\backend\main.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 找到 class LLMPredictionRequest 之前的内容
split_marker = "class LLMPredictionRequest(BaseModel):"
parts = content.split(split_marker)
if len(parts) != 2:
    print("Error finding split marker")
    exit(1)

base_content = parts[0]

new_code = """class LLMPredictionRequest(BaseModel):
    team1_name: str
    team2_name: str
    force_refresh: bool = False

client = OpenAI(
    api_key="sk-f3a841c03faa4f63bf3a45bfbf010edb",
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
        p_text = f"【{t['name']}】\\n"
        p_text += f"FIFA排名：{t.get('fifa_ranking')}\\n"
        p_text += f"主教练：{t.get('coach')}\\n"
        p_text += f"阵型：{t.get('formation')}\\n"
        p_text += f"身价：{t.get('total_value')}\\n"
        p_text += f"平均年龄：{t.get('avg_age')}\\n"
        p_text += "部分核心球员(按综合评分降序)：\\n"
        for p in players[:6]:
            stats_str = ""
            if p.get('stats'):
                stats_str = " | ".join([f"{k}:{v}" for k, v in p['stats'].items()])
            p_text += f"- {p['name']} ({p['position']}, 评分: {p.get('overall_rating')}) : {stats_str}\\n"
        p_text += "\\n"
        return p_text
        
    context = f"你是一个专业的足球赛事分析师和彩票精算师。请基于以下详细的真实数据，对 {team1_name} vs {team2_name} 的比赛进行定性分析。\\n\\n"
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
        cur.execute(f\"\"\"
            INSERT INTO match_predictions (team1, team2, {field_name}, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (team1, team2) DO UPDATE SET {field_name} = EXCLUDED.{field_name}, updated_at = CURRENT_TIMESTAMP
        \"\"\", (req.team1_name, req.team2_name, result))
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
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(base_content + new_code)
