# Yanting Li
# 11/24/2022

import re
import csv

def find_short_context(string, line_num, short_context_list):
    for key in abbr_dict.keys():
        # TODO: change key to the compiled regex (that includes both short and long forms), string is still one line
        key_idx = [m.start() for m in re.finditer(key, string)]
        if len(key_idx) > 0:
            for i in key_idx:
                pre = string[:i].strip()
                post = string[(i+len(key)):].strip()
                tuple = (key, 'short', pre, post, line_num)
                short_context_list.append(tuple)
    return

def find_long_context(string, line_num, long_context_list):
    for value in abbr_dict.values():
        value_idx = [m.start() for m in re.finditer(value, string)]
        if len(value_idx) > 0:
            for i in value_idx:
                pre = string[:i].strip()
                post = string[(i+len(value)):].strip()
                tuple = (value, 'long', pre, post, line_num)
                long_context_list.append(tuple)
    return 

# writing all contexts found in one news into a .csv file
def string_to_csv(string, line_num):
    short_context_list = []
    long_context_list = []
    
    find_short_context(string, line_num, short_context_list)
    find_long_context(string, line_num, long_context_list)
    with open('context.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerows(short_context_list)
        writer.writerows(long_context_list)

    return 

# creating a dict to store short-long word pairs
with open('abbr_list_full.txt', 'r', encoding = 'utf-8') as f:
    lines = f.readlines()

# TODO: check if any short forms can be matched with different long forms
# if yes, maybe get rid of the pairs 

abbr_dict = {}
for i in range(len(lines)):
    if lines[i].startswith('n'):
        continue
    else:
        pair = lines[i].split(": ")
        short = pair[0]
        longlist = [i.strip() for i in re.split('/[a-z]+', pair[1].strip())]
        long = ''.join(longlist)
        abbr_dict[short] = long
    
with open('all_pure.txt', 'r', encoding = 'utf-8') as f:
    line_num = 0
    while True:
        string = f.readline()
        if not string:
            break;
        line_num += 1
        string_to_csv(string, line_num)

