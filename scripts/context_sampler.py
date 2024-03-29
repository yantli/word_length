# randomly selecting 100 word pairs to build our test file containing 10000 contexts
# Yanting Li
# 1/12/2023

import random
import csv
from xml.sax.handler import DTDHandler
import numpy
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)

tokenizer = AutoTokenizer.from_pretrained("TsinghuaAI/CPM-Generate")
model = AutoModelWithLMHead.from_pretrained("TsinghuaAI/CPM-Generate")

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

# loading the new abbr dict we relied on to clean the context
def load_dict(dict_file):
    with open(dict_file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    return abbr_dict

# building a newer abbr dict containing only word pairs left in the cleaned context
def dict_in_context(dict_file, context_file):
    abbr_dict = load_dict(dict_file)
    cleaned_abbr_dict = {}
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            if target_word in abbr_dict.keys():
                cleaned_abbr_dict[target_word] = abbr_dict.get(target_word)
            
    return cleaned_abbr_dict

# generating a list of tuples for each short or long form that consists of:
# 1) word count 2) the word itself, and 3) whether it's a short or long form 
def abbr_freq_ratio_counter(freq_file, dict_file):
    with open(freq_file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

        word_counts = []
        for line in lines:
            line = tuple(line.split())
            word_counts.append(line)

    # in word_counts, item[0] is the count, item[1] is the word, item[2] is whether it's long or short
    shortlist = [item[1] for item in word_counts if item[2] == 'short']
    longlist = [item[1] for item in word_counts if item[2] == 'long']
    abbr_dict = load_dict(dict_file)
    short_list = []
    long_list = []
    for short, long in abbr_dict.items():
        if long in longlist and short in shortlist:
            short_list.append(short)
            long_list.append(long)

    short_freq_dict = {}
    long_freq_dict = {}
    for item in word_counts:
        if item[1] in short_list:
            short_freq_dict[item[1]] = int(item[0])
        if item[1] in long_list:
            long_freq_dict[item[1]] = int(item[0])

    short_count_list = [short_freq_dict.get(short) for short in short_list]
    sorted_long_list = [abbr_dict.get(short_list[i])for i in range(len(short_list))]
    long_count_list = [long_freq_dict.get(long) for long in sorted_long_list]    
    ratio_list = [int(short_count_list[i])/int(long_count_list[i]) for i in range(len(short_count_list))]    

    summary_list = [(short_list[i], short_count_list[i], sorted_long_list[i], long_count_list[i], ratio_list[i]) for i in range(len(short_list))]
    
    return summary_list

def abbr_screener_by_ratio(freq_file, dict_file, context_file, min_count, min_ratio, max_ratio):
    summary_list = abbr_freq_ratio_counter(freq_file, dict_file)
    cleaned_abbr_dict = dict_in_context(dict_file, context_file)
    cleaned_abbr_dict_by_ratio = cleaned_abbr_dict.copy()
    # summary = (short_word, short_count, long_word, long_count, ratio)
    keys = [summary[0] for summary in summary_list if summary[1] > min_count if summary[3] > min_count if min_ratio < summary[4] < max_ratio]
    
    useless_keys = [key for key in cleaned_abbr_dict.keys() if key not in keys]
    for key in useless_keys:
        del cleaned_abbr_dict_by_ratio[key]
    
    ratio_dict = {}
    for short, long in cleaned_abbr_dict_by_ratio.items():
        if short not in problematic_short:
            ratio_dict[short] = long

    return ratio_dict

# further screen abbr by whether the tokenization of either form starts with an "8"
def abbr_screener_by_tokenization(dict_file):
    abbr_dict = load_dict(dict_file)
    new_abbr_dict = abbr_dict.copy()
    short = list([key for key in abbr_dict.keys()])
    short_to_be_thrown = [word for word in short if check_token(word)]
    long = list([value for value in abbr_dict.values()])
    long_to_be_thrown = [word for word in long if check_token(word)]
    for short, long in abbr_dict.items():
        if long in long_to_be_thrown and short not in short_to_be_thrown:
            short_to_be_thrown.append(short) 

    for key in short_to_be_thrown:
        del new_abbr_dict[key]
    
    return new_abbr_dict

# getting the tokenization of each target word
def check_token(target_word):
    # find the tokens of the target word by adding a 。 at the end of it
    # the token for '。' is [8, 12, 4, 3]
    stop_token = ' 8 12 4 3'
    tokens_with_stop = tokenizer.encode(target_word + '。')
    return tokens_with_stop[0] == 8

# save the updated dictionary
def write_new_dict(dict_to_write, file):
    with open(file, 'w', encoding = 'utf-8') as output_f:
        for short, long in dict_to_write.items():
            pair = [short, long]
            output_f.writelines('\t'.join(pair))
            output_f.writelines('\n')

# randomly pick num_to_select of pairs of words from the abbr dict and create a new dict
def pick_pair(dict_file, num_to_select):
    abbr_dict = load_dict(dict_file)
    group_of_items = abbr_dict.keys()
    list_of_random_keys = random.sample(group_of_items, num_to_select)

    sampled_abbr_dict = {}
    for key in list_of_random_keys:
        sampled_abbr_dict[key] = abbr_dict.get(key)
    
    target_words = [key for key in sampled_abbr_dict.keys()] + [value for value in sampled_abbr_dict.values()]

    return target_words

# pick out contexts that contain target words
def context_screener(dict_file, num_to_select, context_file, output_file):
    target_words = pick_pair(dict_file, num_to_select)
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            if target_word in target_words:
                save_context(output_file, row)

# randomly pick 5 contexts for each word, i.e. 10 for each pair, 1000 in total
def randomized_context_picker(input_file, num_to_pick, output_file, min_context_length = False):
    context_dict = {}
    with open(input_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            if target_word in context_dict:
                context_dict[target_word].append(row)
            else:
                context_dict[target_word] = [row]

    for key in context_dict:
        if min_context_length:
            allvalues = context_dict.get(key)
            group_of_items = [value for value in allvalues if len(value[2])>= min_context_length]
        else:
            group_of_items = context_dict.get(key)
        list_of_random_context = random.sample(group_of_items, num_to_pick)
        for context in list_of_random_context:
            save_context(output_file, context)        

def save_context(file, row):
    with open(file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'
    freq_file = '/Users/yanting/Desktop/word_length/abbr_dict/cleaned_abbr_freq.txt'
    context_file = '/Users/yanting/Desktop/word_length/data/context_cleaned.csv'
    # context_screener('/Users/yanting/Desktop/word_length/abbr_dict/equal_toklen_dict.txt', 77, context_file, '/Users/yanting/Desktop/word_length/data/context_equaltoklen_pairs.csv')
    randomized_context_picker('/Users/yanting/Desktop/word_length/data/context_100count_newpairs.csv', 50, '/Users/yanting/Desktop/word_length/data/context_newpairs50longentry.csv')
