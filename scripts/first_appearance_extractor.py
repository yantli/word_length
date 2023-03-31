# for every piece of news, only keep the first appearance of the target words
# 3/8/2023

import csv
abbr_dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'

def load_abbr_dict(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    
    return abbr_dict

def get_alternate_word(abbr_dict_file, target_form, target_word):
    abbr_dict = load_abbr_dict(abbr_dict_file)
    if target_form == 'short':
        alternate_word = abbr_dict[target_word]
    else:
        for short, long in abbr_dict.items():
            if long == target_word:
                alternate_word = short

    return alternate_word

def save_context(row):
    with open('/Users/yanting/Desktop/word_length/data/context_cleaned_firstmention.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    abbr_dict = load_abbr_dict(abbr_dict_file)
    tw_linenum_dict = {}
    tw_row_dict = {}
    values_to_delete = []
    others = []
    with open('/Users/yanting/Desktop/word_length/data/context_cleaned.csv', 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            alternate_word = get_alternate_word(abbr_dict_file, target_form, target_word)

            if target_word not in tw_linenum_dict.keys():
                if alternate_word not in tw_linenum_dict.keys():
                    tw_linenum_dict[target_word] = [line_num]
                    tw_row_dict[target_word] = [row]
                else:
                    if line_num not in tw_linenum_dict.get(alternate_word):
                        tw_linenum_dict[target_word] = [line_num]
                        tw_row_dict[target_word] = [row]
                    else:
                        for value in tw_row_dict.get(alternate_word):
                            if value[4] == line_num:
                                if value[2] >= row[2]:
                                    # values_to_delete.append(value)
                                    tw_linenum_dict.get(alternate_word).remove(line_num)
                                    tw_row_dict.get(alternate_word).remove(value)
                                    tw_linenum_dict[target_word] = [line_num]
                                    tw_row_dict[target_word] = [row]
                                else:
                                    others.append(row)
            else: 
                if line_num not in tw_linenum_dict.get(target_word):
                    if alternate_word not in tw_linenum_dict.keys():
                        tw_linenum_dict.get(target_word).append(line_num)
                        tw_row_dict.get(target_word).append(row)
                    else:
                        if line_num not in tw_linenum_dict.get(alternate_word):
                            tw_linenum_dict.get(target_word).append(line_num)
                            tw_row_dict.get(target_word).append(row)
                        else:
                            for value in tw_row_dict.get(alternate_word):
                                if value[4] == line_num:
                                    if value[2] >= row[2]:
                                        # values_to_delete.append(value)
                                        tw_linenum_dict.get(alternate_word).remove(line_num)
                                        tw_row_dict.get(alternate_word).remove(value)                                    
                                        tw_linenum_dict.get(target_word).append(line_num)
                                        tw_row_dict.get(target_word).append(row)
                                    else:
                                        others.append(row)
                else:
                    for value in tw_row_dict.get(target_word):
                        if value[4] == line_num:
                            if value[2] >= row[2]:
                                # values_to_delete.append(value)
                                tw_row_dict.get(target_word).remove(value)
                                tw_row_dict.get(target_word).append(row)
                            else:
                                others.append(row)

rows_to_print = []
for value in tw_row_dict.values():
    for row in value: 
        # rows_to_print.append(row)
        save_context(row)
