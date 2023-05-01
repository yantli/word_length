# cal_prob using rfutrell/gpt2_wiki40b_zh-cn 
# 04/24/2023

import re
import csv
import numpy
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)

tokenizer = AutoTokenizer.from_pretrained("rfutrell/gpt2_wiki40b_zh-cn")
model = AutoModelWithLMHead.from_pretrained("rfutrell/gpt2_wiki40b_zh-cn")

dict_path = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'
context_file_path = '/Users/yanting/Desktop/word_length/data/context_test.csv'
prob_file_path = '/Users/yanting/Desktop/word_length/probs/test_prob.csv'

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

# making sure pre-context is within 200 characters, and post-context is within 50.
def row_size_standardizer(row):
    target_word = row[0]
    target_form = row[1]
    pre_context = row[2]
    post_context = row[3]
    line_num = row[4]

    if len(pre_context) > 10:
        new_pre_context = pre_context[-10:]
    else:
        new_pre_context = pre_context
    if len(post_context) > 50:
        new_post_context = post_context[:50]
    else: 
        new_post_context = post_context

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

def alternate_row_creater(row):
    alternate_word = get_alternate_word(row[1], row[0])
    if row[1] == 'short':
        alternate_form = 'long'
    else:
        alternate_form = 'short'
    alternate_row = [alternate_word, alternate_form, row[2], row[3], row[4]]
    standardized_alternate_row = row_size_standardizer(alternate_row)

    return standardized_alternate_row

# getting the token(s) of 1) the target word, 2) the tokens of the whole story up to the target word and 3) the tokens of the whole sentence
def get_tokens(target_word, row):
    # find the tokens of the target word by adding a 。 at the end of it
    # the token for '。' is [264]
    stop_token = ' 264'
    tokens_with_stop = tokenizer.encode(target_word + '。')
    end_idx = ' '.join([str(token) for token in tokens_with_stop]).find(stop_token)
    target_tokens_str = ' '.join([str(token) for token in tokens_with_stop])[:end_idx]
    target_tokens = [int(token) for token in target_tokens_str.split()]

    pre_context = row[2]
    pre_context_tokens = tokenizer.encode(pre_context)[:-2]
    post_context = row[3]
    up_to_target_tokens = tokenizer.encode(pre_context + target_word)[:-1]  # getting rid of the [264] at the end

    sent = pre_context + target_word + post_context
    sent_tokens = tokenizer.encode(sent)
 
    return target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens

# check if target word following the pre-context will not be retokenized to something else
def stable_tokenization_checker(target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in up_to_target_tokens])
    return target_tokens == up_to_target_tokens[-len(target_tokens):]

# check if target word in the whole sentence will not be retokenized to something else
def stable_tokenization_checker2(target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in up_to_target_tokens])
    return target_tokens == sent_tokens[len(pre_context_tokens):(len(pre_context_tokens)+len(target_tokens))]

def context_pair_tokenization_checker(target_word, row):
    alt_row = alternate_row_creater(row)
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    alt_target_tokens, alt_pre_context_tokens, alt_up_to_target_tokens, alt_sent_tokens = get_tokens(alt_row[0], alt_row)

    return up_to_target_tokens[:-len(target_tokens)] == alt_up_to_target_tokens[:-len(alt_target_tokens)]

# calculating the probability of each short and long form in the context they appeared
def cal_prob(target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # tok_for_tensor = up_to_target_tokens[-(len(target_tokens)+2):]
    # result = model(torch.tensor(tok_for_tensor))
    # logprobs = torch.log_softmax(result.logits, -1)[:, tuple(tok_for_tensor[1:])].diag()
    result = model(torch.tensor(up_to_target_tokens))
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(up_to_target_tokens[1:])].diag()
    # find the indices of the encountered form:
    # ending_index = len(tok_for_tensor)-1
    ending_index = len(up_to_target_tokens) - 1
    starting_index = ending_index - len(target_tokens)
    logprob = logprobs[starting_index:ending_index].sum()
    
    return logprob

# this is checking whether switching word form will change the tokenization of the context
def clean_rows(rows):
    index_to_throw = []
    index = 0
    while index < len(rows)-2:
        target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(rows[index][0], rows[index])
        alt_target_tokens, alt_pre_context_tokens, alt_up_to_target_tokens, alt_sent_tokens = get_tokens(rows[index+1][0], rows[index+1])

        if up_to_target_tokens[:-len(target_tokens)] != alt_up_to_target_tokens[:-len(alt_target_tokens)]:
            index_to_throw.append(index)
            index_to_throw.append(index+1)
        index += 2 
    index_to_throw = sorted(index_to_throw, reverse = True)

def save_prob(output, prob_file_path):
    with open(prob_file_path, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))

def line_by_line(context_file):
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            row = row_size_standardizer(row)
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            alternate_word = get_alternate_word(target_form, target_word)
            
            # if stable_tokenization_checker(target_word, row) and stable_tokenization_checker(alternate_word, row) and context_pair_tokenization_checker(target_word, row):
            if stable_tokenization_checker(target_word, row) and stable_tokenization_checker(alternate_word, row) and stable_tokenization_checker2(target_word, row) and stable_tokenization_checker2(alternate_word, row) and context_pair_tokenization_checker(target_word, row):
                logprob = cal_prob(target_word, row)
                # alternate_logprob = cal_alternate_prob(target_form, target_word, row)
                alternate_logprob = cal_prob(alternate_word, alternate_row_creater(row))
                # print(alternate_logprob)
                # add them up by torch.logaddexp before the .item()
                disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
                output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
                print(output)
                save_prob(output)
            else:
                output = target_word, target_form, line_num
                # print(output)
            
if __name__ == "__main__":
    line_by_line(context_file_path)
    # cal_in_batch('test_context.csv')
    
