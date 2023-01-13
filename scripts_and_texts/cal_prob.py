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

# calculating the probability of each short and long form in the context they appeared
def cal_prob(target_word, row):
    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(target_word, row)
    result = model(torch.tensor(sent_tokens))
    # TODO: we can replace sent_tokens with a list that contains the tokens of 1000 sentences
    # we can use result.arrange(2*100*10) to structure the tesnor
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(sent_tokens[1:])].diag()
    # find the indices of the encountered form:
    # len(up_to_target_tokens) is the actual length+2 since there is [4, 3] at the end
    ending_index = len(up_to_target_tokens) - 3
    starting_index = ending_index - len(target_tokens)
    logprob = logprobs[starting_index:ending_index].sum()
    
    return logprob

def cal_alternate_prob(target_form, target_word, row):
    new_abbr_dict = load_abbr_dict()
    if target_form == 'short':
        new_target_word = new_abbr_dict[target_word]
    else:
        new_target_word = list(new_abbr_dict.keys())[list(new_abbr_dict.values()).index(target_word)]

    target_tokens, up_to_target_tokens, sent_tokens = get_tokens(new_target_word, row)
    result = model(torch.tensor(sent_tokens))
    logprobs = torch.log_softmax(result.logits, -1)[:, tuple(sent_tokens[1:])].diag()
    ending_index = len(up_to_target_tokens) - 3
    starting_index = ending_index - len(target_tokens)
    alternate_logprob = logprobs[starting_index:ending_index].sum()

    return alternate_logprob

def save_prob(output):
    with open('prob.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(output))


if __name__ == "__main__":
    with open('test_context.csv', 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]
            logprob = cal_prob(target_word, row)
            alternate_logprob = cal_alternate_prob(target_form, target_word, row)
            # add them up by torch.logaddexp before the .item()
            disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
            output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
            save_prob(output)


# if __name__ == "__main__":
    
#     row = ['筹资','short',"根据日本经济新闻在三十日指出,日本政府可能取消外资对日本电报电信公司NTT的最高股权限制,使日本电报电信能够寻求和国际财团的合作关系。  报导指出,日本邮电省将要求成立一个顾问小组,来负责考量有关修改一九八五年的NTT法案、并且希望在明年度向国会提出修正过的法案。  在一九八五年的NTT法案中,限制了外商在这个前国营事业中的投资上限为百分之十九点九,而目前外资在NTT中的持股比例维持在百分之十四。  不过NTT希望这项法令能够松绑,使它得以寻求和亚洲、欧洲与美国的电信企业的合作关系。而在NTT要求解除上限的同时,邮电省则要求NTT必须继续它的服务性角色,也就是说对全日本的国内电话降低费率以作为交换条件。  NTT行政高层曾在本周对此表示反对,他们辩称NTT在国内外的竞争对手,并没面临到日本新近逐渐解除限制的电信市场冲击,而这正是NTT在财务上的一个先天障碍。报导指出,日本政府也将要求NTT对其国内竞争同业开放它的光纤联网。  日本政府是在周五时宣布,将在下月释出NTT一百万股持股,以协助抑止日本政府逐渐增高的债务、并且加速NTT的民营化进程。NTT是从一九八五年开始走向私有化,展开第一次的政府释股行动。  此外,NTT也表示它将发行三十万股新股,以协助它进行收购美国网路公司Verio Inc.的",
#             "。  日本政府在NTT中的持股比例,正在逐渐降低到百分之四十六;报导说,一旦NTT和日本政府持续释股,外资对NTT的持股将很快就会超过百分之二十。",8]
#     target_word = row[0]
#     target_form = row[1]
#     line_num = row[4]
#     logprob = cal_prob(target_word, row)
#     alternate_logprob = cal_alternate_prob(target_form, target_word, row)
#     # add them up by torch.logaddexp before the .item()
#     disjunction_logprob = torch.logaddexp(logprob, alternate_logprob).item() 
#     output = target_word, target_form, logprob.item(), disjunction_logprob, line_num
#     print(output)


# for each context, we need the tokenization with the short form, and the tokenization with the long form
# short: c1 c2 w1 w2 0 0        (the 0 is the padding pattern)
# long:  c1 c2 w1 w2 w3 w4
# need to make sure that c1 c2 are identical for short and long
# tokenizer([sent1, sent2]), padding=True
# the output will give you 'attention_mask' where it has 1 for real tokens and 0 for padding tokens 

# we can use result.arrange(batch_size * 2 * len_of_the_longest_sent) to structure the tesnor

# 1. create short and long sentences
# 2. check whether the tokenization of the forms are unchanged
#  
