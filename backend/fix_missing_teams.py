# -*- coding: utf-8 -*-
"""补充5支缺失球员数据的球队：苏格兰、突尼斯、伊朗、挪威、葡萄牙"""
import psycopg2
from psycopg2.extras import Json

conn = psycopg2.connect(user='postgres', password='002505@Zx', host='127.0.0.1', port=5432, database='postgres')
cur = conn.cursor()

teams_data = {
    '苏格兰': {
        'coach': '克拉克',
        'players': [
            {'name': '冈恩', 'position': '门将', 'age': 28, 'overall_rating': 74},
            {'name': '罗伯逊', 'position': '后卫', 'age': 32, 'overall_rating': 79},
            {'name': '蒂尔尼', 'position': '后卫', 'age': 29, 'overall_rating': 77},
            {'name': '亨德利', 'position': '后卫', 'age': 27, 'overall_rating': 73},
            {'name': '麦肯纳', 'position': '后卫', 'age': 26, 'overall_rating': 72},
            {'name': '波特奥斯', 'position': '后卫', 'age': 25, 'overall_rating': 71},
            {'name': '麦克金', 'position': '中场', 'age': 31, 'overall_rating': 78},
            {'name': '吉尔摩', 'position': '中场', 'age': 25, 'overall_rating': 76},
            {'name': '麦格雷戈', 'position': '中场', 'age': 33, 'overall_rating': 74},
            {'name': '亚当斯', 'position': '前锋', 'age': 29, 'overall_rating': 76},
            {'name': '尚克兰', 'position': '前锋', 'age': 28, 'overall_rating': 74},
            {'name': '戴克斯', 'position': '前锋', 'age': 30, 'overall_rating': 72},
        ]
    },
    '突尼斯': {
        'coach': '卡德里',
        'players': [
            {'name': '达门', 'position': '门将', 'age': 27, 'overall_rating': 73},
            {'name': '塔尔比', 'position': '后卫', 'age': 26, 'overall_rating': 74},
            {'name': '梅里亚', 'position': '后卫', 'age': 29, 'overall_rating': 73},
            {'name': '布隆', 'position': '后卫', 'age': 28, 'overall_rating': 72},
            {'name': '瓦莱里', 'position': '后卫', 'age': 25, 'overall_rating': 71},
            {'name': '阿卜迪', 'position': '后卫', 'age': 27, 'overall_rating': 70},
            {'name': '斯希里', 'position': '中场', 'age': 31, 'overall_rating': 77},
            {'name': '莱杜尼', 'position': '中场', 'age': 28, 'overall_rating': 74},
            {'name': '哈兹里', 'position': '中场', 'age': 33, 'overall_rating': 73},
            {'name': '姆萨克尼', 'position': '前锋', 'age': 27, 'overall_rating': 74},
            {'name': '贾齐里', 'position': '前锋', 'age': 30, 'overall_rating': 73},
            {'name': '哈尼', 'position': '前锋', 'age': 25, 'overall_rating': 71},
        ]
    },
    '伊朗': {
        'coach': '加莱诺埃',
        'players': [
            {'name': '贝兰万德', 'position': '门将', 'age': 33, 'overall_rating': 74},
            {'name': '哈伊萨菲', 'position': '后卫', 'age': 35, 'overall_rating': 73},
            {'name': '穆哈拉米', 'position': '后卫', 'age': 27, 'overall_rating': 72},
            {'name': '卡里米', 'position': '后卫', 'age': 28, 'overall_rating': 71},
            {'name': '雷扎伊安', 'position': '后卫', 'age': 34, 'overall_rating': 70},
            {'name': '哈利勒扎德', 'position': '后卫', 'age': 26, 'overall_rating': 69},
            {'name': '埃扎托拉希', 'position': '中场', 'age': 29, 'overall_rating': 74},
            {'name': '古多斯', 'position': '中场', 'age': 30, 'overall_rating': 75},
            {'name': '贾汉巴赫什', 'position': '中场', 'age': 32, 'overall_rating': 73},
            {'name': '塔雷米', 'position': '前锋', 'age': 33, 'overall_rating': 79},
            {'name': '阿兹蒙', 'position': '前锋', 'age': 31, 'overall_rating': 76},
            {'name': '安萨里法德', 'position': '前锋', 'age': 35, 'overall_rating': 72},
        ]
    },
    '挪威': {
        'coach': '索尔巴肯',
        'players': [
            {'name': '尼兰', 'position': '门将', 'age': 31, 'overall_rating': 76},
            {'name': '厄斯蒂高', 'position': '后卫', 'age': 27, 'overall_rating': 76},
            {'name': '阿耶尔', 'position': '后卫', 'age': 26, 'overall_rating': 74},
            {'name': '梅林', 'position': '后卫', 'age': 28, 'overall_rating': 73},
            {'name': '彼得森', 'position': '后卫', 'age': 29, 'overall_rating': 72},
            {'name': '林内斯', 'position': '后卫', 'age': 25, 'overall_rating': 71},
            {'name': '厄德高', 'position': '中场', 'age': 27, 'overall_rating': 84},
            {'name': '贝格', 'position': '中场', 'age': 28, 'overall_rating': 76},
            {'name': '索尔斯比', 'position': '中场', 'age': 26, 'overall_rating': 74},
            {'name': '哈兰德', 'position': '前锋', 'age': 25, 'overall_rating': 91},
            {'name': '索洛特', 'position': '前锋', 'age': 29, 'overall_rating': 78},
            {'name': '拉尔森', 'position': '前锋', 'age': 26, 'overall_rating': 74},
        ]
    },
    '葡萄牙': {
        'coach': '马丁内斯',
        'players': [
            {'name': '迪奥戈·科斯塔', 'position': '门将', 'age': 26, 'overall_rating': 82},
            {'name': '迪亚斯', 'position': '后卫', 'age': 29, 'overall_rating': 84},
            {'name': '门德斯', 'position': '后卫', 'age': 24, 'overall_rating': 80},
            {'name': '坎塞洛', 'position': '后卫', 'age': 31, 'overall_rating': 82},
            {'name': '佩雷拉', 'position': '后卫', 'age': 28, 'overall_rating': 78},
            {'name': '伊纳西奥', 'position': '后卫', 'age': 24, 'overall_rating': 77},
            {'name': 'B·费尔南德斯', 'position': '中场', 'age': 31, 'overall_rating': 87},
            {'name': 'B·席尔瓦', 'position': '中场', 'age': 31, 'overall_rating': 86},
            {'name': '维蒂尼亚', 'position': '中场', 'age': 25, 'overall_rating': 84},
            {'name': '内维斯', 'position': '中场', 'age': 28, 'overall_rating': 80},
            {'name': 'C罗', 'position': '前锋', 'age': 41, 'overall_rating': 82},
            {'name': '莱昂', 'position': '前锋', 'age': 26, 'overall_rating': 84},
            {'name': '若塔', 'position': '前锋', 'age': 29, 'overall_rating': 80},
        ]
    },
}

for team_name, data in teams_data.items():
    cur.execute('SELECT id FROM teams WHERE name = %s', (team_name,))
    row = cur.fetchone()
    if not row:
        print(f'WARN: {team_name} not found')
        continue
    team_id = row[0]

    cur.execute('UPDATE teams SET coach = %s WHERE id = %s', (data['coach'], team_id))
    cur.execute('DELETE FROM players_detailed WHERE team_id = %s', (team_id,))
    cur.execute('DELETE FROM players WHERE team_id = %s', (team_id,))

    for p in data['players']:
        cur.execute('''
            INSERT INTO players_detailed (team_id, name, age, position, club, is_starter, overall_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (team_id, p['name'], p['age'], p['position'], '', False, p['overall_rating']))
        cur.execute('''
            INSERT INTO players (team_id, name, position, age, jersey_number, is_key_player)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (team_id, p['name'], p['position'], p['age'], None, False))

    # 设置首发 (4-3-3)
    cur.execute('''
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
    ''', (team_id,))

    print(f'{team_name}: {len(data["players"])} players, starters set')

conn.commit()
cur.close()
conn.close()
print('Done!')
