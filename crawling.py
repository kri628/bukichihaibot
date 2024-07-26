import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql

df = pd.DataFrame(columns=['id', 'name', 'sub', 'special', 'inked'])
con = pymysql.connect(host='127.0.0.1', user='test', password='test01', db='splatoon3_db', charset='utf8')

tables = ['ch_area', 'ch_tower', 'ch_fish', 'ch_clam', 'x_area', 'x_tower', 'x_fish', 'x_clam']

urls = ['https://stat.ink/entire/weapons3/bankara_challenge/area?season=8',
        'https://stat.ink/entire/weapons3/bankara_challenge/yagura?season=8',
        'https://stat.ink/entire/weapons3/bankara_challenge/hoko?season=8',
        'https://stat.ink/entire/weapons3/bankara_challenge/asari?season=8',
        'https://stat.ink/entire/weapons3/xmatch/area?season=8',
        'https://stat.ink/entire/weapons3/xmatch/yagura?season=8',
        'https://stat.ink/entire/weapons3/xmatch/hoko?season=8',
        'https://stat.ink/entire/weapons3/xmatch/asari?season=8',
        ]

td_id = ['cceb8b0e', '1e9ee576', 'eb9d0cd1', 'd1de5d11', '3dbecd3f', 'f72372fb', 'd4985b86', '9b132dcb']

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
           "Accept-Language": "ja"}

for i in range(8):
    html = requests.get(urls[i], headers=headers).text
    # print(html)

    soup = BeautifulSoup(html, 'html.parser')
    # trs = soup.select('#w-9935112e-1 > table > tbody > tr')   # English
    trs = soup.select(f'#w-{td_id[i]}-1 > table > tbody > tr')     # japanese
    # print(trs)

    cur = con.cursor()
    sql = f"INSERT INTO {tables[i]} (id, name, sub, special, use_rate, win_rate, mkill, deth, assi, kilassi, ink) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    if trs:
        cur.execute(f"TRUNCATE TABLE {tables[i]}")

    for tr in trs:
        weapon_id = int(tr.attrs['data-key'].strip())
        name = tr.select_one('td:nth-child(1) > a').text.strip()
        sub = tr.select_one('td:nth-child(2)').attrs['data-sort-value'].strip()
        special = tr.select_one('td:nth-child(3)').attrs['data-sort-value'].strip()
        use_rate = float(tr.select_one('td:nth-child(5) > div > div').text.strip().strip('%')) / 100
        win_rate = float(tr.select_one('td:nth-child(6)').attrs['data-sort-value'].strip()) / 100
        kill = float(tr.select_one('td:nth-child(7)').attrs['data-sort-value'].strip())
        deth = float(tr.select_one('td:nth-child(8)').attrs['data-sort-value'].strip())
        assi = float(tr.select_one('td:nth-child(12)').attrs['data-sort-value'].strip())
        kilassi = float(tr.select_one('td:nth-child(14)').attrs['data-sort-value'].strip())
        ink = float(tr.select_one('td:nth-child(19)').attrs['data-sort-value'].strip())

        if weapon_id < 121 or weapon_id > 132:  # execpt side order weapons
            print(weapon_id, name, sub, special, use_rate, win_rate, kill, deth, assi, kilassi, ink)
            cur.execute(sql, (weapon_id, name, sub, special, use_rate, win_rate, kill, deth, assi, kilassi, ink))

con.commit()
con.close()
