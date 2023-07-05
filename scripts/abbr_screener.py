# Take all abbr pairs and build a new dict with:
# 1) pairs with both short and long appeared in all contexts found by count_freq_2.py
# 2) pairs with short freq > 10, long freq > 10, and with 0.1 < long_short_ratio < 10
# 3) pairs without tokenization artifact (i.e. the "8" in front of the token)

# Yanting Li
# 12/13/2022

import re
import csv
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)

tokenizer = AutoTokenizer.from_pretrained("TsinghuaAI/CPM-Generate")
model = AutoModelWithLMHead.from_pretrained("TsinghuaAI/CPM-Generate")

# generating the dict containing all short-long word pairs
def create_abbr_dict(dict_file):
    if dict_file == '/Users/yanting/Desktop/word_length/abbr_dict/abbr_dict_full.txt':
        with open(dict_file, 'r', encoding = 'utf-8') as f:
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

    else:
        with open(dict_file, 'r', encoding = 'utf-8') as f:
            lines = f.readlines()
        abbr_dict = {}
        for i in range(len(lines)):
            pair = lines[i].split()
            short = pair[0]
            long = pair[1]
            abbr_dict[short] = long

    return abbr_dict

# taking in a txt file with word counts of each target word
# generating a list of tuples for each short or long form that consists of:
# 1) word count 2) the word itself, and 3) whether it's a short or long form 
def create_abbr_freq(freq_file):
    with open(freq_file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

        word_counts = []
        for line in lines:
            line = tuple(line.split())
            word_counts.append(line)

    return word_counts
        
# checking whether both short and long form of a concept showed up in the text:
def abbr_pair_checker(dict_file, freq_file):
    abbr_dict = create_abbr_dict(dict_file)
    word_counts = create_abbr_freq(freq_file)

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
# def single_token_checker():
#     full_short_list, full_long_list, short_word_list, long_word_list, summary_list = abbr_pair_checker()
#     short_tokens = short_word_list.copy()
#     with open('all_tokenized.txt', 'r', encoding = 'utf-8') as f:
#         while True:
#             string = f.readline()
#             if not string:
#                 break;
#             else:
#                 for token in short_tokens:
#                     if token in string:
#                         short_tokens.remove(token)
#     return short_tokens

# generating a new dict without the unpaired words:
def update_abbr_dict(dict_file, freq_file, min_ratio, max_ratio):
    summary_list = abbr_pair_checker(dict_file, freq_file)[4]
    abbr_dict = create_abbr_dict(dict_file)
    # summary = (short_word, short_count, long_word, long_count, ratio)
    keys = [summary[0] for summary in summary_list if summary[1] > 10 if summary[3] > 10 if min_ratio < summary[4] < max_ratio]
    
    useless_keys = [key for key in abbr_dict.keys() if key not in keys]
    problematic_short = ['上图', '乔峰', '二毛', '优品', '公益', 
                        '共市', '印报', '吐纳', '工装', '成府', 
                        '探子', '西大', '县府', '中大', '人大', 
                        '国标', '留美', '电联', '孤寡', '家教'] 

    # short_in_long =    ['效颦', '棒喝', '海货', '精油', '复关',
    #                     '蚁防', '领台', '升幅', '阪神', '读博',
    #                     '港人', '包商', '票选', '密报', '裂伤',
    #                     '报备', '外贸', '放贷', '影评', '要角', 
    #                     '内销', '葬仪', '十届', '金市', '金价', 
    #                     '内资', '名导', '开发协会', '港警',
    #                     '剧评', '脱贫', '港岛', '空港', '车市',
    #                     '港大', '赛地', '军报', '三产', '办展', 
    #                     '军代表', '植棉', '外宣', '油市',
    #                     '产需', '还贷', '加幅', '港客', '雪联',   
    #                     '川大', '产供', '护鸟', 
    #                     '受教', '空运', '二产', '一监', '电站',
    #                     '寸照', '史著', '一产', '鲜蔬', 
    #                     '陆架', '养教', '防保', '儿麻', '体模',
    #                     '校建', '民警', '乐评', '弹速',
    #                     '体语', '影带', '融政', '摄制', '余资',
    #                     '港商', '差旅', '像带', '泳技', '校企',
    #                     '地价', '外销', '路警', '计陷', '影业',
    #                     '持平', '话机', '息率', '耗能', '泳协',
    #                     '泌乳', '关检', '观展', '速生', '影技',
    #                     '要项', '名记', '影圈', '津城',
                        
    #                     '中央美院', '计生户', '尤杯赛', '汤杯赛',]
    useless_keys += problematic_short
    
    for key in abbr_dict.keys():
        if tokenizer.encode(key)[0] == 8 or tokenizer.encode(abbr_dict.get(key))[0] == 8:
            useless_keys.append(key)

    new_abbr_dict = {}
    for key, value in abbr_dict.items():
        if key not in useless_keys:
            new_abbr_dict[key] = value
    
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
def write_new_dict(dict_file, dict):
    with open(dict_file, 'w', encoding = 'utf-8') as output_f:
        for short, long in dict.items():
            pair = [short, long]
            output_f.writelines('\t'.join(pair))
            output_f.writelines('\n')

if __name__ == "__main__":
    # write_paired_abbr_freq()
    # write_throw_out_list()
    original_abbr_dict = '/Users/yanting/Desktop/word_length/abbr_dict/clue_w_topic_new_abbr_dict.txt'
    freq_file = '/Users/yanting/Desktop/word_length/abbr_dict/clue_w_topic_cleaned_freq.txt'
    new_abbr_dict = update_abbr_dict(original_abbr_dict, freq_file, 0.1, 10)
    write_new_dict('/Users/yanting/Desktop/word_length/abbr_dict/clue_w_topic_cleaned_dict_by_ratio.txt', new_abbr_dict)
