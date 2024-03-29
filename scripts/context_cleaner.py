# Take all contexts found by count_freq_2.py and only keep:
# 1) texts with target words in the new abbr list generated by abbr_screener.py
# 2) texts with target words appearing with non-empty pre-context and post-context
# 3) texts with target words that are tokenized by CPM in the context as its original tokenization as an individual word
# Yanting Li
# 12/20/2022

import re
import csv
import numpy
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)
# from abbr_screener import update_abbr_dict

tokenizer = AutoTokenizer.from_pretrained("TsinghuaAI/CPM-Generate")
model = AutoModelWithLMHead.from_pretrained("TsinghuaAI/CPM-Generate")

# load the designated dictionary
def load_abbr_dict(dict_file):
    with open(dict_file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    return abbr_dict

# completing 1), return True if we should keep the line
def screener_one(dict_file, target_word, row):
    # new_abbr_dict = update_abbr_dict(0.1, 10)
    abbr_dict = load_abbr_dict(dict_file)
    target_word = row[0]
    return target_word in abbr_dict.keys() or target_word in abbr_dict.values()
       
# completing 2), return True if we should keep the line. 
# The len(row) == 5 should be changed to len(row) == 6 if we are dealing with cluecomm_w_topic contexts
def screener_two(row):
    return len(row) == 6 and len(row[2].strip('！？｡。＃＄％＆＇（）()＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞“”" ')) > 0 and len(row[3].strip('！？｡。＃＄％＆＇（）()＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞“”" ')) > 0

# getting the token(s) of 1) the target word, 2) the tokens of the whole story up to the target word and 3) the tokens of the whole sentence
def get_tokens(target_word, row):
    # find the tokens of the target word by adding a 。 at the end of it
    # the token for '。' is [8, 12, 4, 3]
    stop_token = ' 8 12 4 3'
    tokens_with_stop = tokenizer.encode(target_word + '。')
    end_idx = ' '.join([str(token) for token in tokens_with_stop]).find(stop_token)
    if tokens_with_stop[0] == 8:
        target_tokens_str = ' '.join([str(token) for token in tokens_with_stop])[2:end_idx]
    else:
        target_tokens_str = ' '.join([str(token) for token in tokens_with_stop])[:end_idx]
    target_tokens = [int(token) for token in target_tokens_str.split()]

    pre_context = row[2]
    post_context = row[3]

    up_to_target_tokens = tokenizer.encode(pre_context + target_word)

    sent = pre_context + target_word + post_context
    sent_tokens = tokenizer.encode(sent)

    return target_tokens, up_to_target_tokens, sent_tokens

# completing 3), return True if we should keep the line
# TODO: this needs to be fixed since it didn't specify the position of the target token
def screener_three(target_word, row):
    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in sent_tokens])
        
def save_context(cleaned_file, row):
    with open(cleaned_file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/clue_w_topic_new_abbr_dict.txt'
    # context_file = '/Users/yanting/Desktop/word_length/data/context_2.csv'
    context_file = '/Users/yanting/Desktop/word_length/data/cluecomm_w_topic_context.csv'
    cleaned_file = '/Users/yanting/Desktop/word_length/data/cluecomm_w_topic_context_cleaned.csv'
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            if screener_one(dict_file, target_word, row) and screener_two(row):
                if screener_three(target_word, row):
                    save_context(cleaned_file, row)
                    print(row)

            