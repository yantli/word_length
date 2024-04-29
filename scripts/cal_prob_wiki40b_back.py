# cal_prob using yantli/gpt2_wiki40b_zh-cn_backward
# 1/3/2024

import re
import csv
import numpy
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)

tokenizer = AutoTokenizer.from_pretrained("yantli/backward_wiki40b_zh-cn")
model = AutoModelWithLMHead.from_pretrained("yantli/backward_wiki40b_zh-cn")

# load the new_abbr_dict
def load_abbr_dict(dict_path):
    with open(dict_path, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    return abbr_dict

# making sure pre-context is within 50 characters, and post-context is within 200, and then reverse the string
def row_size_standardizer(row):
    target_word = row[0][::-1]
    target_form = row[1]
    pre_context = row[2]
    post_context = row[3]
    line_num = row[4]

    if len(pre_context) > 50:
        new_pre_context = pre_context[-50:][::-1]
    else:
        new_pre_context = pre_context[::-1]
    if len(post_context) > 200:
        new_post_context = post_context[:200][::-1]
    else: 
        new_post_context = post_context[::-1]

    new_row = [target_word, target_form, new_pre_context, new_post_context, line_num]

    return new_row

# get the alternate form
def get_alternate_word(dict_path, target_form, target_word):
    abbr_dict = load_abbr_dict(dict_path)
    if target_form == 'short':
        alternate_word = abbr_dict[target_word]
    else:
        for short, long in abbr_dict.items():
            if long == target_word:
                alternate_word = short

    return alternate_word

def alternate_row_creater(dict_path, row):
    alternate_word = get_alternate_word(dict_path, row[1], row[0][::-1])
    if row[1] == 'short':
        alternate_form = 'long'
    else:
        alternate_form = 'short'
    alternate_row = [alternate_word[::-1], alternate_form, row[2], row[3], row[4]]

    return alternate_row

# getting the token(s) of 1) the target word, 2) the tokens of the whole story up to the target word and 3) the tokens of the whole sentence
def get_tokens(target_word_rev, row):
    target_tokens = tokenizer.encode(target_word_rev)

    pre_context_rev = row[2]
    post_context_rev = row[3]
    post_context_rev_tokens = tokenizer.encode(post_context_rev)
    back_to_target_tokens = tokenizer.encode(post_context_rev + target_word_rev)

    sent_rev = post_context_rev + target_word_rev + pre_context_rev
    sent_rev_tokens = tokenizer.encode(sent_rev)
 
    return target_tokens, post_context_rev_tokens, back_to_target_tokens, sent_rev_tokens

# check if target word following the pre-context will not be retokenized to something else
def stable_tokenization_checker(target_word_rev, row):
    target_tokens, post_context_rev_tokens, back_to_target_tokens, sent_rev_tokens = get_tokens(target_word_rev, row)
    return target_tokens == back_to_target_tokens[-len(target_tokens):]

# check if target word in the whole sentence will not be retokenized to something else
def stable_tokenization_checker2(target_word_rev, row):
    target_tokens, post_context_rev_tokens, back_to_target_tokens, sent_rev_tokens = get_tokens(target_word_rev, row)
    return target_tokens == sent_rev_tokens[len(post_context_rev_tokens):(len(post_context_rev_tokens)+len(target_tokens))]

def context_pair_tokenization_checker(dict_path, target_word_rev, row):
    alt_row = alternate_row_creater(dict_path, row)
    target_tokens, post_context_rev_tokens, back_to_target_tokens, sent_rev_tokens = get_tokens(target_word_rev, row)
    alt_target_tokens, alt_post_context_rev_tokens, alt_back_to_target_tokens, alt_sent_rev_tokens = get_tokens(alt_row[0], alt_row)

    return back_to_target_tokens[:-len(target_tokens)] == alt_back_to_target_tokens[:-len(alt_target_tokens)]

# calculating the probability of each short and long form in the context they appeared
def cal_prob(target_word_rev, row):
    target_tokens, post_context_rev_tokens, back_to_target_tokens, sent_rev_tokens = get_tokens(target_word_rev, row)
    # tok_for_tensor = up_to_target_tokens[-(len(target_tokens)+2):]
    # result = model(torch.tensor(tok_for_tensor))
    # logprobs = torch.log_softmax(result.logits, -1)[:, tuple(tok_for_tensor[1:])].diag()
    result = model(torch.tensor(back_to_target_tokens))
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(back_to_target_tokens[1:])].diag()
    # find the indices of the encountered form:
    # ending_index = len(tok_for_tensor)-1
    ending_index = len(back_to_target_tokens) - 1
    starting_index = ending_index - len(target_tokens)
    logprob = logprobs[starting_index:ending_index].sum()
    
    return logprob

def save_prob(output, prob_file):
    with open(prob_file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))

def line_by_line(context_file, dict_path, prob_file):
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            row = row_size_standardizer(row)
            target_word_rev = row[0]
            target_form = row[1]
            line_num = row[4]
            alt_word_rev = get_alternate_word(dict_path, target_form, target_word_rev[::-1])[::-1]
            alt_row = alternate_row_creater(dict_path, row)

            # if stable_tokenization_checker(target_word, row) and stable_tokenization_checker(alternate_word, row) and context_pair_tokenization_checker(target_word, row):
            if stable_tokenization_checker(target_word_rev, row) and stable_tokenization_checker(alt_word_rev, alt_row) and stable_tokenization_checker2(target_word_rev, row) and stable_tokenization_checker2(alt_word_rev, alt_row) and context_pair_tokenization_checker(dict_path, target_word_rev, row):
                logprob = cal_prob(target_word_rev, row)
                alternate_logprob = cal_prob(alt_word_rev, alt_row)
                disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
                output = target_word_rev[::-1], target_form, logprob.item(), disjunction_logprob, line_num
                print(output)
                save_prob(output, prob_file)
            else:
                output = target_word_rev[::-1], target_form, line_num
            
if __name__ == "__main__":
    context_file = '/Users/yanting/Desktop/word_length/data/context_10000_freq_samples.csv'
    dict_path = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'
    prob_file = '/Users/yanting/Desktop/word_length/probs/prob_fwiki_oldpairs200.csv'
    line_by_line(context_file, dict_path, prob_file)