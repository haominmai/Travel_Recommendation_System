import csv
import random
import pandas as pd


def get_random_rec(cur_index):
    recommend_list = []
    with open('data.csv', 'r', encoding='utf-8') as f:
        csv_1 = csv.reader(f)
        index = 0
        for line in csv_1:
            if index == 0:
                index += 1
                continue
            recommend_list.append(line)
    df = pd.DataFrame(recommend_list, columns=[
        '0','1','2','3','4','5','6','7','8','9','10'
    ])
    j = df[(df['9'] == 'No Such Information')].index
    df.drop(j).reset_index()
    while True:
        i = random.randint(0, len(df))
        if i != cur_index:
            return df.iloc[i], i
