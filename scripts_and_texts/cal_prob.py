# calculating the probability of each short and long form in the context they appeared 
# 12/13/2022

import re
import csv
import numpy
import torch
from transformers import (
    TextGenerationPipeline, 
    AutoTokenizer, 
    AutoModelWithLMHead
)

tokenizer = AutoTokenizer.from_pretrained("TsinghuaAI/CPM-Generate")
model = AutoModelWithLMHead.from_pretrained("TsinghuaAI/CPM-Generate")

# load the new_abbr_dict
def load_abbr_dict():
    with open('new_abbr_dict.txt', 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    return abbr_dict

# making sure the length of the whole news is shorter than 1265
def check_len(row):
    return len(row[0]) + len(row[2]) <= 1200

def alternate_row_creater(row):
    alternate_word = get_alternate(row[1], row[0])
    if row[1] == 'short':
        alternate_form = 'long'
    else:
        alternate_form = 'short'
    alternate_row = [alternate_word, alternate_form, row[2], row[3], row[4]]

    return alternate_row

# getting the token(s) of 1) the target word, 2) the tokens of the whole story up to the target word and 3) the tokens of the whole sentence
def get_tokens(target_word, row):
    # find the tokens of the target word by adding a 。 at the end of it
    # the token for '。' is [8, 12, 4, 3]
    stop_token = ' 8 12 4 3'
    tokens_with_stop = tokenizer.encode(target_word + '。')
    end_idx = ' '.join([str(token) for token in tokens_with_stop]).find(stop_token)

    pre_context = row[2]
    post_context = row[3]

    if tokens_with_stop[0] == 8:
        target_tokens_str = ' '.join([str(token) for token in tokens_with_stop])[2:end_idx]
    
    else:
        target_tokens_str = ' '.join([str(token) for token in tokens_with_stop])[:end_idx]
    
    target_tokens = [int(token) for token in target_tokens_str.split()]
    up_to_target_tokens = tokenizer.encode(pre_context + target_word)

    if up_to_target_tokens[-(len(target_tokens)+3)] == 8:
        up_to_target_tokens = tokenizer.encode(pre_context + target_word)[:-(len(target_tokens)+3)] + target_tokens + [4, 3]

    sent = pre_context + target_word + post_context
    sent_tokens = tokenizer.encode(sent)

    return target_tokens, up_to_target_tokens, sent_tokens

# calculating the probability of each short and long form in the context they appeared
def cal_prob(target_word, row):
    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    result = model(torch.tensor(up_to_target_tokens))
    # TODO: we can replace up_to_target_tokens with a list that contains the tokens of 1000 sentences
    # we can use result.arrange(2*100*10) to structure the tesnor
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(up_to_target_tokens[1:])].diag()
    # find the indices of the encountered form:
    # len(up_to_target_tokens) is the actual length+2 since there is [4, 3] at the end
    ending_index = len(up_to_target_tokens) - 3
    starting_index = ending_index - len(target_tokens)
    logprob = logprobs[starting_index:ending_index].sum()
    
    return logprob

# get the alternate form
def get_alternate(target_form, target_word):
    abbr_dict = load_abbr_dict()
    if target_form == 'short':
        alternate_word = abbr_dict[target_word]
    else:
        for short, long in abbr_dict.items():
            if long == target_word:
                alternate_word = short

    return alternate_word

# check if alternate word in the context will not be retokenized to something else
def alternate_token_checker(alternate_word, row):
# TODO: this needs to be fixed since it didn't specify the position of the target token
    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(alternate_word, row)
    return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in sent_tokens])


def cal_alternate_prob(target_form, target_word, row):
    alternate_word = get_alternate(target_form, target_word)
    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(alternate_word, row)
    
    result = model(torch.tensor(up_to_target_tokens))
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(up_to_target_tokens[1:])].diag()
    ending_index = len(up_to_target_tokens) - 3
    starting_index = ending_index - len(target_tokens)
    alternate_logprob = logprobs[starting_index:ending_index].sum()

    return alternate_logprob

def save_prob(output):
    with open('prob.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))

def new_way():
    rows = []
    discard_rows = []
    with open('context_1000sample.csv', 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            alternate_word = get_alternate(target_form, target_word)
            # check when the alternate form is inserted in the news, whether it keeps its original tokenization
            if alternate_token_checker(alternate_word, row):
                rows.append(row)
                alternate_row = alternate_row_creater(row)
                rows.append(alternate_row)
            else:
                discard_rows.append(row)

    # every row_token ends with [4, 3], so we need to get rid of it
    target_tokens = [get_tokens(row[0], row)[0] for row in rows]
    row_tokens = [get_tokens(row[0], row)[1][:-2] for row in rows]

    index_to_throw = []
    index = 0
    while index < len(target_tokens)-2:
        target_token_len = len(target_tokens[index])
        alternate_token_len = len(target_tokens[index+1])
        if row_tokens[index][:-(target_token_len)] != row_tokens[index+1][:-(alternate_token_len)]:
            index_to_throw.append(index)
            index_to_throw.append(index+1)
        index += 2 
    index_to_throw = sorted(index_to_throw, reverse = True)
    
    for index in index_to_throw:
        del rows[index]
        del target_tokens[index]
        del row_tokens[index]

    max_length = max([len(row_token) for row_token in row_tokens])

    # max_length is 6392, and then 5336, 4662, 4425
    # row_tokens = [row_token for row_token in row_tokens if len(row_token) < 5000]

    # result.arrange(len(rows) * max_length) 

    # padding
    row_tokens = [row_token+[5]*(max_length - len(row_token)) for row_token in row_tokens if len(row_token) < max_length]
    result = model(torch.tensor(row_tokens))           


def old_way():
    with open('context_1000sample.csv', 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            alternate_word = get_alternate(row[1], row[0])
            
            if check_len(row):
                if alternate_token_checker(alternate_word, row):
                    logprob = cal_prob(target_word, row)
                    alternate_logprob = cal_alternate_prob(target_form, target_word, row)
                    print(alternate_logprob)
                    # add them up by torch.logaddexp before the .item()
                    disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
                    output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
                    print(output)
                else:
                    output = target_word, target_form, line_num
                    print(output)
                save_prob(output)

if __name__ == "__main__":
    old_way()
    
# if __name__ == "__main__":

#     target_word = row[0]
#     target_form = row[1]
#     line_num = row[4]
#     # check_len(row)

#     alternate_word = get_alternate(row[1], row[0])
#     if alternate_token_checker(alternate_word, row):
#         logprob = cal_prob(target_word, row)
#         alternate_logprob = cal_alternate_prob(target_form, target_word, row)
#         # add them up by torch.logaddexp before the .item()
#         disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
#         output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
#     else:
#         output = target_word, target_form, line_num
#     print(output)



# for each context, we need the tokenization with the short form, and the tokenization with the long form
# short: c1 c2 w1 w2 0 0        (the 0 is the padding pattern)
# long:  c1 c2 w1 w2 w3 w4
# need to make sure that c1 c2 are identical for short and long
# the output will give you 'attention_mask' where it has 1 for real tokens and 0 for padding tokens 

# we can use result.arrange(batch_size * 2 * len_of_the_longest_sent) to structure the tesnor
# replace up_to_target_tokens with a list that contains the tokens of 1000 sentences
# we can use result.arrange(2*100*10) to structure the tesnor

# 1. create short and long sentences (Done)
# 2. check whether the tokenization of the forms are unchanged (Done)


# result = model(torch.tensor(list_of_sents))
# logprobs = torch.log_softmax(result.logits, -1)[:, tuple(sent_tokens[1:])].diag()
