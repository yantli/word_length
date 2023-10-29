# explore how to train a model to calculate backward predictability
# potential model to use: https://huggingface.co/fnlp/cpt-base
# 8/5/2023

# Yanting Li

import torch

from modeling_cpt import CPTForConditionalGeneration
from transformers import BertTokenizer, pipeline
tokenizer = BertTokenizer.from_pretrained("fnlp/cpt-base")
model = CPTForConditionalGeneration.from_pretrained("fnlp/cpt-base")

# example provided by developer for text generation:
# input_ids = tokenizer.encode("北京是[MASK]的首都", return_tensors='pt')
# pred_ids = model.generate(input_ids, num_beams=4, max_length=20)
# print(tokenizer.convert_ids_to_tokens(pred_ids[0]))

input_tokens = tokenizer.encode("北京是[MASK]的首都")
input_ids = tokenizer.encode("北京是[MASK]的首都", return_tensors='pt')
mask_idx = input_tokens.index(103)
result = model(input_ids)
# if we do result.logits.shape, it should be equal to the length of input_ids
# probability the model assigns to each word in the mask pos
logprobs = torch.log_softmax(result.logits, -1)
token_to_check = tokenizer.encode(char_to_check)[1]
char_logprob = logprobs[0][mask_idx,token_to_check]

logprobs = torch.log_softmax(result.logits, -1)[0][:, tuple(input_tokens)].diag()


