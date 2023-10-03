import random
import pandas as pd
import numpy as np
import pymysql

con = pymysql.connect(host='127.0.0.1', user='test', password='test01', db='splatoon3_db', charset='utf8')
cur = con.cursor()

# df = pd.read_csv('./weapondb.csv')
# print(data)
# name = set(data['name'])
# weapon_id = set(df['id'])
# print(name)
ink_threshold = 800.0

sql = 'select P.id, P.name, (ch_area + ch_tower + ch_fish + ch_clam + x_area + x_tower + x_fish + x_clam) / 8 as sum from (select ch_area.id, ch_area.name, ch_area.ink as ch_area, A.ink as ch_tower, B.ink as ch_fish, C.ink as ch_clam,  D.ink as x_area, E.ink as x_tower, F.ink as x_fish, G.ink as x_clam  from ch_area left join ch_tower as A on ch_area.id = A.id  left join ch_fish as B on A.id = B.id  left join ch_clam as C on B.id = C.id  left join x_area as D on C.id = D.id  left join x_tower as E on D.id = E.id  left join x_fish as F on E.id = F.id  left join x_clam as G on F.id = G.id) P;'
cur.execute(sql)
rows = cur.fetchall()
ink_df = pd.DataFrame(rows, columns=['id', 'name', 'inked'])
# print(ink_df)
weapon_id = set(ink_df['id'])

cur.execute('select * from name')
rows = cur.fetchall()
name_df = pd.DataFrame(rows, columns=['id', 'name', 'alias'])


def isInkable(id_list):
    m_inked = np.mean(ink_df.iloc[id_list]['inked'])
    # print(df.iloc[id_list]['name'], m_inked)
    if m_inked > ink_threshold:
        return True
    else:
        return False


def isNotEqual(prev_result, result, num):
    if not prev_result:
        return True
    if len(prev_result) != len(result):
        return True

    for i in range(num):
        if result[i] == prev_result[i]:
            return False
    return True


def random_buki(non_dup, num):
    if non_dup:
        result = random.sample(weapon_id, num)
    else:
        result = [random.randint(0, 101) for i in range(num)]

    return result


def getOpResult(num, prev_result, settings):
    min_inked = settings.get('min-inked')
    non_dup = settings.get('non-dup')

    result = random_buki(non_dup, num)

    if min_inked:
        while True:
            if isInkable(result):
                break
            result = random_buki(non_dup, num)

    while True:
        if isNotEqual(prev_result, result, num):
            break
        result = random_buki(non_dup, num)

    weapon = name_df.iloc[result]['alias']
    # print(weapon, result, prev_result)

    return weapon, result


def getPrResult(n, settings):
    min_inked = settings.get('min-inked')
    non_dup = settings.get('non-dup')

    result_b = random_buki(non_dup, n)
    result_y = random_buki(non_dup, n)

    if min_inked:
        while True:
            if isInkable(result_b):
                break
            result_b = random_buki(non_dup, n)

        while True:
            if isInkable(result_y):
                break
            result_y = random_buki(non_dup, n)

    weapon_b = name_df.iloc[result_b]['alias']
    weapon_y = name_df.iloc[result_y]['alias']

    return weapon_b, weapon_y
