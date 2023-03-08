# trying out glm-10b-chinese model (https://huggingface.co/THUDM/glm-10b-chinese)
# 2/28/2023

import csv
import numpy
import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("THUDM/glm-10b-chinese", trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained("THUDM/glm-10b-chinese", trust_remote_code=True)
model = model.half().cuda()

def get_tokens(target_word, row):
    # find the tokens of the target word. Usually the token will be [50002, ..., ..., ..., 50000]
    target_tokens = tokenizer.encode(target_word)[1:-1]
    pre_context = row[2]
    pre_context_tokens = tokenizer.encode(pre_context)[1:-1]
    post_context = row[3]
    up_to_target_tokens = tokenizer.encode(pre_context + target_word)[1:-1]
    sent = pre_context + target_word + post_context
    sent_tokens = tokenizer.encode(sent)[1:-1]
 
    return target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens

def cal_prob(target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # this is to make sure that cuda is used instead of cpu
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    sent_tensor = torch.tensor(up_to_target_tokens).to(device)
    sent_tensor = sent_tensor.view(1, -1)
    # the above code returned "tensor([[50002,  1847,  9425, 43361, 50000]], device='cuda:0')" for "这是北京大学。".
    # input_ids = sent_tensor.to(torch.int64)
    # with torch.no_grad():
    #     outputs = model(input_ids=input_ids)
    result = model(sent_tensor)
    # result.logits.size() should return [0, num of tokens in the input, 50048]
    # for the first word of the sentence: logprob = torch.log_softmax(result.logits, -1)[0, 0, sent[1]]
    logprobs = torch.log_softmax(result.logits, -1)[0, :, tuple(sent[1:])].diag()

    ending_index = len(up_to_target_tokens) - 1
    starting_index = ending_index - len(target_tokens)
    logprob = logprobs[starting_index:ending_index].sum()
    
    return logprob

# sent = tokenizer.encode("这是北京大学。")

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

# making sure pre-context is within 200 characters, and post-context is within 50.
def row_size_standardizer(row):
    target_word = row[0]
    target_form = row[1]
    pre_context = row[2]
    post_context = row[3]
    line_num = row[4]

    if len(pre_context) > 100:
        new_pre_context = pre_context[-100:]
    else:
        new_pre_context = pre_context
    if len(post_context) > 50:
        new_post_context = post_context[:50]
    else: 
        new_post_context = post_context

    new_row = [target_word, target_form, new_pre_context, new_post_context, line_num]

    return new_row

# get the alternate form
def get_alternate_word(target_form, target_word):
    abbr_dict = load_abbr_dict()
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

def stable_tokenization_checker(target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in up_to_target_tokens])
    return target_tokens == up_to_target_tokens[-len(target_tokens):]

# check if target word in the whole sentence will not be retokenized to something else
def stable_tokenization_checker2(lm, target_word, row):
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    # return ' '.join([str(x) for x in target_tokens]) in ' '.join([str(x) for x in up_to_target_tokens])
    return target_tokens == sent_tokens[len(pre_context_tokens):(len(pre_context_tokens)+len(target_tokens))]

def context_pair_tokenization_checker(target_word, row):
    alt_row = alternate_row_creater(row)
    target_tokens, pre_context_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    alt_target_tokens, alt_pre_context_tokens, alt_up_to_target_tokens, alt_sent_tokens = get_tokens(lm, alt_row[0], alt_row)

    return up_to_target_tokens[:-len(target_tokens)] == alt_up_to_target_tokens[:-len(alt_target_tokens)]

def save_prob(output):
    with open('test_prob.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))

def line_by_line(file):
    with open(file, 'r', encoding = 'utf-8') as f:
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
                alternate_logprob = cal_prob(alternate_word, alternate_row_creater(row))
                disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
                output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
                print(output)
                save_prob(output)
            else:
                output = target_word, target_form, line_num
                print(output)
            
if __name__ == "__main__":
    line_by_line('test_context.csv')
