import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql

df = pd.DataFrame(columns=['id', 'name', 'sub', 'special', 'inked'])
con = pymysql.connect(host='127.0.0.1', user='test', password='test01', db='splatoon3_db', charset='utf8')

tables = ['ch_area', 'ch_tower', 'ch_fish', 'ch_clam', 'x_area', 'x_tower', 'x_fish', 'x_clam']

urls = ['https://stat.ink/entire/weapons3/bankara_challenge/area?season=5',
        'https://stat.ink/entire/weapons3/bankara_challenge/yagura?season=5',
        'https://stat.ink/entire/weapons3/bankara_challenge/hoko?season=5',
        'https://stat.ink/entire/weapons3/bankara_challenge/asari?season=5',
        'https://stat.ink/entire/weapons3/xmatch/area?season=5',
        'https://stat.ink/entire/weapons3/xmatch/yagura?season=5',
        'https://stat.ink/entire/weapons3/xmatch/hoko?season=5',
        'https://stat.ink/entire/weapons3/xmatch/asari?season=5',
        ]

td_id = ['62c7a71a', 'f871828c', 'd2cb7372', '64db7551', 'e67a5baa', 'bb4e997d', '47e9c315', '72b2ac33']

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

        print(weapon_id, name, sub, special, use_rate, win_rate, kill, deth, assi, kilassi, ink)
        # df.loc[weapon_id] = [weapon_id, name, sub, special, inked]

        cur.execute(sql, (weapon_id, name, sub, special, use_rate, win_rate, kill, deth, assi, kilassi, ink))

    # print(df)
    # df.to_csv('./weapondb.csv', mode='w', index=False)

con.commit()
con.close()
