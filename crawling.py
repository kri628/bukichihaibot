import requests
from bs4 import BeautifulSoup
import pandas as pd

df = pd.DataFrame(columns=['id', 'name', 'sub', 'special', 'inked'])

url = 'https://stat.ink/entire/weapons3/bankara_challenge/area?season=5'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
           "Accept-Language": "ja"}
html = requests.get(url, headers=headers).text
# print(html)

soup = BeautifulSoup(html, 'html.parser')
# trs = soup.select('#w-9935112e-1 > table > tbody > tr')   # English
trs = soup.select('#w-aea0bceb-1 > table > tbody > tr')     # japanese
# print(trs[0])

for tr in trs:
    weapon_id = int(tr.attrs['data-key'].strip())
    name = tr.select_one('td:nth-child(1) > a').text.strip()
    sub = tr.select_one('td:nth-child(2)').attrs['data-sort-value'].strip()
    special = tr.select_one('td:nth-child(3)').attrs['data-sort-value'].strip()
    inked = float(tr.select_one('td:nth-child(20)').attrs['data-sort-value'].strip())

    # print(weapon_id, name, sub, special, inked)
    df.loc[weapon_id] = [weapon_id, name, sub, special, inked]

print(df)
df.to_csv('./weapondb.csv', mode='w', index=False)


