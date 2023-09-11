import random
import pandas as pd
import numpy as np

df = pd.read_csv('./weapondb.csv')
# print(data)
# name = set(data['name'])
weapon_id = set(df['id'])
# print(name)
ink_threshold = 230.0


def isInkable(id_list):
    m_inked = np.mean(df.iloc[id_list]['inked'])
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


def getOpResult(num, prev_result, min_inked):
    result = random.sample(weapon_id, num)

    if min_inked:
        while True:
            if isInkable(result):
                break
            result = random.sample(weapon_id, num)

    while True:
        if isNotEqual(prev_result, result, num):
            break
        result = random.sample(weapon_id, num)

    weapon = df.iloc[result]['name']
    # print(weapon, result, prev_result)

    return weapon, result


def getPrResult(n, min_inked):
    result_b = random.sample(weapon_id, n)
    result_y = random.sample(weapon_id, n)

    if min_inked:
        while True:
            if isInkable(result_b):
                break
            result_b = random.sample(weapon_id, n)

        while True:
            if isInkable(result_y):
                break
            result_y = random.sample(weapon_id, n)

    weapon_b = df.iloc[result_b]['name']
    weapon_y = df.iloc[result_y]['name']

    return weapon_b, weapon_y
