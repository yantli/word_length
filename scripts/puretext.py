# Convert texts downloaded from Chinese Gigaword Firth Ed to:
# 1) pure texts
# 2) tokenized texts
# Yanting Li
# Written on 11/12/2022

# adding texts from cluecorpus, which is in .json format
# only used training part of the CLUEcorpus community data

import jieba
import json

# from os import listdir
# from os.path import isfile, join

# mypath = '/Users/yanting/Downloads/cmn_gw_5/data/afp_cmn'
# filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# file = gunzip()


def read_in_txt_file(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

    newlines = []
    for i in range(len(lines)):
        if lines[i] == '<P>\n':
            while lines[i+1] != '</P>\n': 
                newlines.append(lines[i+1].strip('\n'))
                i = i+1
        elif lines[i] == '</TEXT>\n':
            newlines.append('\n')
    newlines = ''.join(newlines)
    return newlines

def save_pure_text(output_file, newlines):
    with open(output_file, 'a', encoding = 'utf-8') as output_f:
        output_f.write(newlines)
        output_f.writelines('\n')

def save_tokenized_text(newlines):
    seg_list = jieba.cut(newlines, cut_all = False)
    newlines = ' '.join(seg_list)
    with open('zbn_cmn_tokenized.txt', 'w', encoding = 'utf-8') as output_f:
        output_f.writelines(newlines)

def read_in_json_file(input_file, output_file):
    with open(input_file, 'r') as f:
        for line in f:
            object = json.loads(line)
            content = object.get('content')
            save_pure_text(output_file, content)

if __name__ == "__main__":
    # save_pure_text(read_in_txt_file('zbnall.txt'))
    # save_tokenized_text(read_in_txt_file('zbnall.txt'))
    path_to_json_file = '/Users/yanting/Desktop/word_length/corpora/cluecorpus/community_text/web_text_zh_train.json'
    output = '/Users/yanting/Desktop/word_length/corpora/cluecorpus/community_text/cluecommunity.txt'
    read_in_json_file(path_to_json_file, output)
