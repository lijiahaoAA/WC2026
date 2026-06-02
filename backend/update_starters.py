import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))

def update_starters():
    conn = psycopg2.connect(
        user="postgres", 
        password=os.getenv("DB_PASSWORD", "postgres"), 
        host="127.0.0.1", 
        port=5432, 
        database="postgres"
    )
    cur = conn.cursor()
    
    # 1. Reset all to False
    cur.execute("UPDATE players_detailed SET is_starter = FALSE;")
    
    cur.execute("SELECT id FROM teams;")
    teams = cur.fetchall()
    
    for (team_id,) in teams:
        # We want 1 GK, 4 DF, 3 MF, 3 FW. If some are missing, fill up to 11.
        starters = []
        
        # Get GK
        cur.execute("SELECT id FROM players_detailed WHERE team_id = %s AND position = '门将' ORDER BY overall_rating DESC NULLS LAST LIMIT 1;", (team_id,))
        gk = cur.fetchall()
        starters.extend([r[0] for r in gk])
        
        # Get DF
        cur.execute("SELECT id FROM players_detailed WHERE team_id = %s AND position = '后卫' ORDER BY overall_rating DESC NULLS LAST LIMIT 4;", (team_id,))
        df = cur.fetchall()
        starters.extend([r[0] for r in df])
        
        # Get MF
        cur.execute("SELECT id FROM players_detailed WHERE team_id = %s AND position = '中场' ORDER BY overall_rating DESC NULLS LAST LIMIT 3;", (team_id,))
        mf = cur.fetchall()
        starters.extend([r[0] for r in mf])
        
        # Get FW
        cur.execute("SELECT id FROM players_detailed WHERE team_id = %s AND position = '前锋' ORDER BY overall_rating DESC NULLS LAST LIMIT 3;", (team_id,))
        fw = cur.fetchall()
        starters.extend([r[0] for r in fw])
        
        # If we have less than 11 (maybe lacking forwards or midfielders), fill with remaining top rated players
        if len(starters) < 11:
            shortage = 11 - len(starters)
            if starters:
                placeholders = ','.join(['%s'] * len(starters))
                query = f"SELECT id FROM players_detailed WHERE team_id = %s AND id NOT IN ({placeholders}) AND position != '教练' ORDER BY overall_rating DESC NULLS LAST LIMIT %s;"
                cur.execute(query, (team_id, *starters, shortage))
            else:
                cur.execute("SELECT id FROM players_detailed WHERE team_id = %s AND position != '教练' ORDER BY overall_rating DESC NULLS LAST LIMIT %s;", (team_id, shortage))
            extra = cur.fetchall()
            starters.extend([r[0] for r in extra])
            
        if starters:
            placeholders = ','.join(['%s'] * len(starters))
            cur.execute(f"UPDATE players_detailed SET is_starter = TRUE WHERE id IN ({placeholders});", starters)
            
    conn.commit()
    cur.close()
    conn.close()
    print("Starters updated successfully based on formation!")

if __name__ == "__main__":
    update_starters()
