# randomly selecting 100 word pairs to build our test file containing 1000 contexts
# Yanting Li

import random
import csv


with open('new_abbr_dict.txt', 'r', encoding = 'utf-8') as f:
    lines = f.readlines()
abbr_dict = {}
for i in range(len(lines)):
    pair = lines[i].split()
    short = pair[0]
    long = pair[1]
    abbr_dict[short] = long

group_of_items = abbr_dict.keys()
num_to_select = 100
list_of_random_keys = random.sample(group_of_items, num_to_select)

sampler_abbr_dict = {}
for key in list_of_random_keys:
    sampler_abbr_dict[key] = abbr_dict.get(key)

target_words = list(sampler_abbr_dict.keys()) + list(sampler_abbr_dict.values())

def save_context(row):
    with open('context_cleaned_1000sample.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

with open('context_cleaned.csv', 'r', encoding = 'utf-8') as f:
    filereader = csv.reader(f, delimiter = ',')
    for row in filereader:
        target_word = row[0]
        if target_word in target_words:
            save_context(row)