import random
import pandas as pd
import numpy as np

df = pd.read_csv('./weapondb.csv')
# print(data)
# name = set(data['name'])
weapon_id = set(df['id'])
# print(name)
ink_threshold = 250.0


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

    weapon = df.iloc[result]['name']
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

    weapon_b = df.iloc[result_b]['name']
    weapon_y = df.iloc[result_y]['name']

    return weapon_b, weapon_y
