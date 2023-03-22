import csv
import random


def get(cur_index):
    recommend_list = []
    with open('data.csv', 'r') as f:
        csv_1 = csv.reader(f)
        index = 0
        for line in csv_1:
            if index == 0:
                index += 1
                continue
            recommend_list.append(line)
    while True:
        i = random.randint(0, len(recommend_list))
        if i != cur_index:
            return recommend_list[i], i

print(get(1))