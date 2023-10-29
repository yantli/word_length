# reverse the texts of the wiki_zh dataset on huggingface (https://huggingface.co/datasets/shaowenchen/wiki_zh/viewer/default/train?p=2)
# use the dataset to finetune the xlnet model chinese-xlnet-base (https://huggingface.co/hfl/chinese-xlnet-base)
# using the cpt environment

# 10/22/2023

import os
import sys
import torch
import numpy as np
import pandas as pd
from datasets import load_dataset

import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import AutoTokenizer,DataCollatorForLanguageModeling,AutoModelForCausalLM, TrainingArguments, Trainer

os.environ["CUDA_VISIBLE_DEVICES"]="0"


# preprocess data
dataset = load_dataset("shaowenchen/wiki_zh", split="train")
dataset = dataset.train_test_split(test_size=0.2)

# Reverse the order of training texts in each example
reversed_dataset = dataset.map(
    lambda examples: {'text': [''.join(x.split()[1:])[::-1] for x in examples['text']]},
    batched=True,
    num_proc=4,
)

# init tokenizer
tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-xlnet-base")

# tokenize dataset
def preprocess_function(examples):
    return tokenizer([" ".join(x) for x in examples["text"]])

tokenized_dataset = reversed_dataset.map(
    preprocess_function,
    batched=True,
    num_proc=4,
)

train_dataset = tokenized_dataset['train']
test_dataset = tokenized_dataset['test']

tokenizer.pad_token = tokenizer.eos_token
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)


model = AutoModelForCausalLM.from_pretrained("hfl/chinese-xlnet-base").to("cuda:0")

training_args = TrainingArguments(
    output_dir='xlnet-finetuned',
    learning_rate=5e-5,
    weight_decay = 0.01,
    warmup_ratio=0.1,
    lr_scheduler_type = 'linear',
    evaluation_strategy = 'epoch',
    logging_strategy = 'steps',
    logging_steps = 1000,
    save_strategy='epoch'
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=data_collator,
)

trainer.train()