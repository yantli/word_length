# Convert abbr list to:
# abbr form + full form pair, stripping all POS tags
# Yanting Li
# Written on 11/21/2022

import re
import pprint
# def read_in_file(file):
with open('abbr_list_full.txt', 'r', encoding = 'utf-8') as f:
    lines = f.readlines()

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

# for short, long in abbr_dict.items():
#         pair = [short, long]
#         print('\t'.join(pair))

with open('abbr_uniq.txt', 'w', encoding = 'utf-8') as output_f:
    for short, long in abbr_dict.items():
        pair = [short, long]
        output_f.writelines('\t'.join(pair))
        output_f.writelines('\n')