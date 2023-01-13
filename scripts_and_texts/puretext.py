# Convert texts downloaded from Chinese Gigaword Firth Ed to:
# 1) pure texts
# 2) tokenized texts
# Yanting Li
# Written on 11/12/2022

import jieba

# from os import listdir
# from os.path import isfile, join

# mypath = '/Users/yanting/Downloads/cmn_gw_5/data/afp_cmn'
# filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# file = gunzip()


def read_in_file(file):
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

def save_pure_text(newlines):
    with open('zbn_cmn_pure.txt', 'w', encoding = 'utf-8') as output_f:
        output_f.writelines(newlines)

def save_tokenized_text(newlines):
    seg_list = jieba.cut(newlines, cut_all = False)
    newlines = ' '.join(seg_list)
    with open('zbn_cmn_tokenized.txt', 'w', encoding = 'utf-8') as output_f:
        output_f.writelines(newlines)

if __name__ == "__main__":
    save_pure_text(read_in_file('zbnall.txt'))
    save_tokenized_text(read_in_file('zbnall.txt'))