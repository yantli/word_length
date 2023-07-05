# trying to use the trained ngrams to calculate probability
# https://github.com/kpu/kenlm/blob/master/python/example.py
# 5/22/2023

import csv
import kenlm
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)
tokenizer = AutoTokenizer.from_pretrained("TsinghuaAI/CPM-Generate")
binary_file = "/Users/yanting/Desktop/word_length/ngrams/cmn_cpm_3gram.binary"
model = kenlm.LanguageModel(binary_file)

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

def get_alternate_word(dict_file, target_form, target_word):
    abbr_dict = load_abbr_dict(dict_file)
    if target_form == 'short':
        alternate_word = abbr_dict[target_word]
    else:
        for short, long in abbr_dict.items():
            if long == target_word:
                alternate_word = short

    return alternate_word

def alternate_row_creater(dict_file, row):
    alternate_word = get_alternate_word(dict_file, row[1], row[0])
    if row[1] == 'short':
        alternate_form = 'long'
    else:
        alternate_form = 'short'
    alternate_row = [alternate_word, alternate_form, row[2], row[3], row[4]]

    return alternate_row

def cpm_tokenizer(row):
    target_word = row[0]
    pre_context = row[2]
    post_context = row[3]
    tw_tokens = tokenizer.encode(target_word)
    tw_tokenized = [tokenizer.decode(token) for token in tw_tokens[:-2]]
    context_tokens = tokenizer.encode(pre_context)
    context_tokenized = [tokenizer.decode(token) for token in context_tokens[:-2]]
    up_to_tw_tokens = tokenizer.encode(pre_context + target_word)
    up_to_tw_tokenized = [tokenizer.decode(token) for token in up_to_tw_tokens[:-2]]
    sent_tokens = tokenizer.encode(pre_context + target_word + post_context)
    sent_tokenized = [tokenizer.decode(token) for token in sent_tokens[:-2]]

    return tw_tokenized, context_tokenized, up_to_tw_tokenized, sent_tokenized

# check if target word following the pre-context will not be retokenized to something else
def stable_tokenization_checker(row):
    tw_tokenized, context_tokenized, up_to_tw_tokenized, sent_tokenized = cpm_tokenizer(row)
    return tw_tokenized == up_to_tw_tokenized[-len(tw_tokenized):]

# check if target word in the whole sentence will not be retokenized to something else
def stable_tokenization_checker2(row):
    tw_tokenized, context_tokenized, up_to_tw_tokenized, sent_tokenized = cpm_tokenizer(row)
    return tw_tokenized == sent_tokenized[len(context_tokenized):(len(context_tokenized)+len(tw_tokenized))]

def context_pair_tokenization_checker(row):
    alt_row = alternate_row_creater(dict_file, row)
    tw_tokenized = cpm_tokenizer(row)[0]
    alt_tw_tokenized = cpm_tokenizer(alt_row)[0]
    return cpm_tokenizer(row)[2][:-len(tw_tokenized)] == cpm_tokenizer(alt_row)[2][:-len(alt_tw_tokenized)]

def cal_prob(row):
    tw_tokenized = cpm_tokenizer(row)[0]
    len_target_word = len(tw_tokenized)
    
    context_tokenized = cpm_tokenizer(row)[1]
    state = kenlm.State()
    model.BeginSentenceWrite(state)
    for token in context_tokenized:
        state_new = kenlm.State()
        # print(token)
        model.BaseScore(state, token, state_new)
        state = state_new
    
    # print(state)
    accum = 0
    for token in tw_tokenized:
        state_new = kenlm.State()
        # print(token)
        accum += model.BaseScore(state, token, state_new)
        # print(accum)
        state = state_new
    
    return accum

def save_prob(prob_file, output):
    with open(prob_file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))

def line_by_line(context_file, dict_file, prob_file):
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            alt_word = get_alternate_word(dict_file, target_form, target_word)
            alt_row = alternate_row_creater(dict_file, row)
            if stable_tokenization_checker(row) and stable_tokenization_checker(alt_row) and stable_tokenization_checker2(row) and stable_tokenization_checker2(alt_row) and context_pair_tokenization_checker(row):
                # print(row)
                logprob = cal_prob(row)
                alternate_logprob = cal_prob(alt_row)
                disjunction_logprob = torch.logaddexp(torch.tensor(logprob), torch.tensor(alternate_logprob)).item() 
                output = target_word, target_form, logprob, disjunction_logprob, line_num
                print(output)
                save_prob(prob_file, output)
            else:
                output = target_word, target_form, line_num
                print(output)

if __name__ == "__main__":
    # context_file = '/Users/yanting/Desktop/word_length/data/context_10000_freq_samples.csv'
    # dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'
    # prob_file = '/Users/yanting/Desktop/word_length/probs/prob_trigram_oldpair.csv'
    context_file = '/Users/yanting/Desktop/word_length/data/cluecomm_context_117count.csv'
    dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/clue_new_abbr_dict.txt'
    prob_file = '/Users/yanting/Desktop/word_length/probs/prob_trigram_clue117.csv'
    line_by_line(context_file, dict_file, prob_file)