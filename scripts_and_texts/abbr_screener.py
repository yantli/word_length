# Take all abbr pairs and build a new dict with:
# 1) pairs with both short and long appeared in all contexts found by count_freq_2.py
# 2) pairs with short freq > 10, long freq > 10, and with 0.1 < long_short_ratio < 10

# Yanting Li
# 12/13/2022

import re
import csv

# generating the dict containing all short-long word pairs
def create_abbr_dict():
    with open('abbr_list_full.txt', 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

    abbr_dict = {}
    for i in range(len(lines)):
        if lines[i].startswith('n'):
            continue
        else:
            pair = lines[i].split(": ")
            short = pair[0]
            long = ''.join([i.strip() for i in re.split('/[a-z]+', pair[1].strip())])
            if short in abbr_dict.keys():
                del abbr_dict[short]
            else:
                abbr_dict[short] = long

    # deleting short forms that share the same long form:
    seen = set()
    duplicated = []
    for short in abbr_dict.keys():
        if abbr_dict[short] in seen:
            duplicated.append(abbr_dict[short])
        else:
            seen.add(abbr_dict[short])
    key_to_be_deleted = [short for short in abbr_dict.keys() if abbr_dict[short] in duplicated]
    
    for short in key_to_be_deleted:
        del abbr_dict[short] 
    
    return abbr_dict

# generating a list of tuples for each short or long form that consists of:
# 1) word count 2) the word itself, and 3) whether it's a short or long form 
def create_abbr_freq():
    with open('abbr_freq.txt', 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

        word_counts = []
        for line in lines:
            line = tuple(line.split())
            word_counts.append(line)

    return word_counts
        
# checking whether both short and long form of a concept showed up in the text:
def abbr_pair_checker():
    abbr_dict = create_abbr_dict()
    word_counts = create_abbr_freq()

    # in word_counts, item[0] is the count, item[1] is the word, item[2] is whether it's long or short
    full_short_list = [item[1] for item in word_counts if item[2] == 'short']
    full_long_list = [item[1] for item in word_counts if item[2] == 'long']

    short_word_list = [short for short in full_short_list if abbr_dict.get(short) in full_long_list]
    long_word_list = [abbr_dict.get(short) for short in short_word_list]
    
    short_freq_dict = {}
    long_freq_dict = {}
    for item in word_counts:
        if item[1] in short_word_list:
            short_freq_dict[item[1]] = int(item[0])
        if item[1] in long_word_list:
            long_freq_dict[item[1]] = int(item[0])
    
    short_count_list = [short_freq_dict.get(short) for short in short_word_list]    
    long_count_list = [long_freq_dict.get(long) for long in long_word_list]    
    ratio_list = [int(short_count_list[i])/int(long_count_list[i]) for i in range(len(short_count_list))]    

    summary_list = [(short_word_list[i], short_count_list[i], long_word_list[i], long_count_list[i], ratio_list[i]) for i in range(len(short_word_list))]
    
    unseen_short = [short for short in abbr_dict.keys() if short not in full_short_list] 

    return full_short_list, full_long_list, short_word_list, long_word_list, summary_list, unseen_short

def write_paired_abbr_freq():
    summary_list = abbr_pair_checker()[4]
    with open('abbr_freq.csv', 'w', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = '\t')
        writer.writerows(summary_list)

# words to be thrown out because their matching short/long form is not in the text
def find_unpaired_words():
    full_short_list, full_long_list, short_word_list, long_word_list, summary_list, unseen_short = abbr_pair_checker()
    unpaired_short = list(set(full_short_list) - set(short_word_list)) # 1961
    unpaired_long = list(set(full_long_list) - set(long_word_list)) # 397
    
    return unpaired_short, unpaired_long

# check if short forms are treated as one single token (by jieba)
def single_token_checker():
    full_short_list, full_long_list, short_word_list, long_word_list, summary_list = abbr_pair_checker()
    short_tokens = short_word_list.copy()
    with open('all_tokenized.txt', 'r', encoding = 'utf-8') as f:
        while True:
            string = f.readline()
            if not string:
                break;
            else:
                for token in short_tokens:
                    if token in string:
                        short_tokens.remove(token)
    return short_tokens

# generating a new dict without the unpaired words:
def update_abbr_dict(min_ratio, max_ratio):
    summary_list = abbr_pair_checker()[4]
    abbr_dict = create_abbr_dict()
    new_abbr_dict = abbr_dict.copy()
    # summary = (short_word, short_count, long_word, long_count, ratio)
    keys = [summary[0] for summary in summary_list if summary[1] > 10 if summary[3] > 10 if min_ratio < summary[4] < max_ratio]
    
    useless_keys = [key for key in abbr_dict.keys() if key not in keys]
    problematic_short = ['??????', '??????', '??????', '??????', '??????', 
                         '??????', '??????', '??????', '??????', '??????', 
                         '??????', '??????', '??????', '??????', '??????',
                         '??????', '??????', '??????', '??????', '??????', 
                         '??????', '??????', 
                         '??????', '??????', '??????', '??????', '??????',
                         '??????', '??????', '??????', '??????', '??????', 
                         '??????', '??????', '??????', '??????', '??????', 
                         '??????', '??????', '????????????', '??????',
                         '??????', '??????', '??????', '??????', '??????',
                         '??????', '??????', '??????', '??????', '??????', 
                         '?????????', '?????????', '??????', '??????', '??????',
                         '??????', '??????', '??????', '????????????', 
                         '??????', '??????', '??????', '??????', '?????????', 
                         '??????', '??????', '??????', '?????????', '?????????']
    useless_keys += problematic_short

    for key in useless_keys:
        del new_abbr_dict[key]
    
    return new_abbr_dict

# def update_abbr_dict_old():
#     abbr_dict = create_abbr_dict()
#     new_abbr_dict = abbr_dict.copy()
#     unpaired_short, unpaired_long = find_unpaired_words()
#     unseen_short = abbr_pair_checker()[5]
#     short_to_be_thrown_out = unpaired_short.copy()
#     for long in unpaired_long:
#         for short in abbr_dict.keys():
#             if abbr_dict[short] == long:
#                 short_to_be_thrown_out.append(short)
    
#     # add words that are screened out according to the criteria in abbr_freq_reader.R
#     with open('abbr_unbalanced10.csv', 'r', encoding = 'utf-8') as f:
#             filereader = csv.reader(f, delimiter = ',')
#             for row in filereader:
#                 short = row[0]
#                 short_to_be_thrown_out.append(short)
    
#     short_to_be_thrown_out += unseen_short

#     # short_tokens = single_token_checker()
#     # short_to_be_thrown_out += short_tokens

#     for short in short_to_be_thrown_out:
#         if short in new_abbr_dict.keys():
#             del new_abbr_dict[short]
    
#     return new_abbr_dict

# writing the list of words to be thrown out into a .txt file:
def write_throw_out_list():
    unpaired_short, unpaired_long = find_unpaired_words()
    # short_tokens = single_token_checker()
    unseen_short = abbr_pair_checker()[5]

    with open('abbr_throw_out.txt', 'w', encoding = 'utf-8') as f:
        # f.writelines('untokenized_short_tokens:')
        # f.writelines('\n')
        # f.writelines('\n'.join(short_tokens))  
        # f.writelines('\n')
        f.writelines('unpaired_short_forms:')
        f.writelines('\n')
        f.writelines('\n'.join(unpaired_short))
        f.writelines('\n')
        f.writelines('unpaired_long_forms:')
        f.writelines('\n')
        f.writelines('\n'.join(unpaired_long))
        f.writelines('unseen_short_forms:')
        f.writelines('\n')
        f.writelines('\n'.join(unseen_short))

# write remaining pairs into a .txt
def write_new_dict():
    with open('new_abbr_dict.txt', 'w', encoding = 'utf-8') as output_f:
        new_abbr_dict = update_abbr_dict(0.1, 10)
        for short, long in new_abbr_dict.items():
            pair = [short, long]
            output_f.writelines('\t'.join(pair))
            output_f.writelines('\n')

if __name__ == "__main__":
    # write_paired_abbr_freq()
    # write_throw_out_list()
    # new_abbr_dict = update_abbr_dict(0.1, 10)
    write_new_dict()
